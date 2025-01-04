import argparse
import io
import math
import os
import re
import shutil
import subprocess
import sys
import wave

import tqdm


def get_video_framerate(video_path: str) -> int:
    result = subprocess.run([
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ], stdout=subprocess.PIPE)
    return int(result.stdout.decode().strip().split("/")[0])


class Audacity:

    def __init__(self):
        self.tofile: io.TextIOWrapper
        self.fromfile: io.TextIOWrapper
        self.eol: str

    def __enter__(self):
        if sys.platform == 'win32':
            toname = '\\\\.\\pipe\\ToSrvPipe'
            fromname = '\\\\.\\pipe\\FromSrvPipe'
            self.eol = '\r\n\0'
        else:
            toname = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
            fromname = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
            self.eol = '\n'
        try:
            self.tofile = open(toname, "w")
        except FileNotFoundError:
            sys.exit("Error: Audacity not running")
        self.fromfile = open(fromname, "rt")
        return self

    def send_command(self, command):
        """Send a single command."""
        self.tofile.write(command + self.eol)
        self.tofile.flush()

    def get_response(self):
        """Return the command response."""
        result = ''
        line = ''
        while True:
            result += line
            line = self.fromfile.readline()
            if line == '\n' and len(result) > 0:
                break
        return result

    def do(self, command):
        """Send one command, and return the response."""
        self.send_command(command)
        response = self.get_response()
        return response
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tofile.close()
        self.fromfile.close()


def get_tempdir() -> str:
    tempdir = os.path.join(os.path.dirname(__file__), "tmp")
    os.makedirs(tempdir, exist_ok=True)
    return tempdir


def is_same_tempdir(video_path: str, tempdir: str) -> bool:
    same = False
    if os.path.exists(os.path.join(tempdir, "meta.txt")):
        with open("meta.txt", "r", encoding="utf8") as file:
            same = file.read() == os.path.realpath(video_path)
        if not same:
            shutil.rmtree(tempdir)
    os.makedirs(tempdir, exist_ok=True)
    with open(os.path.join(tempdir, "meta.txt"), "w", encoding="utf8") as file:
        file.write(os.path.realpath(video_path))
    return same


def extract_frames(video_path: str, tempdir: str):
    subprocess.Popen([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-stats",
        "-i", video_path,
        os.path.join(tempdir, "framesin", "%09d.bmp"),
    ]).wait()


def format_dynamic_command(command: str, t: int) -> str:
    c = command
    for m in reversed(list(re.finditer(r"\{([^\}]+)\}", c))):
        c = c[:m.start()] + str(eval(m.group(1))) + c[m.end():]
    return c


def process(video_path: str, filter_path: str, output_path: str):
    tempdir = get_tempdir()
    same = is_same_tempdir(video_path, tempdir)
    if os.path.isdir(os.path.join(tempdir, "framesin")) and not same:
        shutil.rmtree(os.path.join(tempdir, "framesin"))
    if not os.path.isdir(os.path.join(tempdir, "framesin")):
        os.makedirs(os.path.join(tempdir, "framesin"))
        extract_frames(video_path, tempdir)
    if os.path.exists(os.path.join(tempdir, "framesout")):
        shutil.rmtree(os.path.join(tempdir, "framesout"))
    os.makedirs(os.path.join(tempdir, "framesout"), exist_ok=True)
    with open(filter_path, "r") as file:
        f = lambda l: not (l.strip() == "" or l.startswith("#"))
        filter_commands = list(filter(f, file.read().strip().split("\n")))
    fps = get_video_framerate(video_path)
    with Audacity() as au3:
        for i, image_name in enumerate(tqdm.tqdm(os.listdir(os.path.join(tempdir, "framesin")))):
            image_path = os.path.join(tempdir, "framesin", image_name)
            with open(image_path, "rb") as file:
                data = file.read()
            with wave.open(os.path.join(tempdir, "input.wav"), "wb") as file:
                file.setnchannels(1)
                file.setsampwidth(1)
                file.setframerate(44100)
                file.writeframesraw(data)
            au3.do(f"SelectAll: ")
            au3.do(f"RemoveTracks: ")
            au3.do(f"Import2: Filename={os.path.realpath(os.path.join(tempdir, 'input.wav'))}")
            au3.do(f"SelectAll: ")
            for command in filter_commands:
                au3.do(format_dynamic_command(command, i/fps))
            au3.do(f"Export2: Filename={os.path.realpath(os.path.join(tempdir, 'output.wav'))}")
            subprocess.Popen([
                "ffmpeg",
                "-hide_banner",
                "-loglevel", "error",
                "-i", os.path.join(tempdir, "output.wav"),
                "-c:a", "pcm_mulaw",
                "-f", "u8",
                os.path.join(tempdir, "output.ulaw"),
                "-y",
            ]).wait()
            with open(os.path.join(tempdir, "output.ulaw"), "rb") as f:
                data = f.read()
            with open(image_path, "rb") as f:
                buffer = f.read(128)
            with open(os.path.join(tempdir, "framesout", image_name), "wb") as f:
                f.write(buffer)
                f.write(data[len(buffer):])
    subprocess.Popen([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-stats",
        "-r", str(get_video_framerate(video_path)),
        "-i", os.path.join(tempdir, "framesout", "%09d.bmp"),
        "-pix_fmt", "yuv420p",
        output_path,
        "-y",
    ]).wait()
    os.startfile(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("filter_path", help="Path to the filter file")
    parser.add_argument("output_path", help="Path to the output file")
    args = parser.parse_args()
    process(args.video_path, args.filter_path, args.output_path)


if __name__ == "__main__":
    main()