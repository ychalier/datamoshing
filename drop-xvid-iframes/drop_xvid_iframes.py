import argparse
import json
import os
import sys
import subprocess
from pathlib import Path

import av


def ffmpeg(*args: list[str]):
    subprocess.Popen([
        "ffmpeg",
        "-loglevel", "quiet",
        "-stats",
        "-hide_banner",
        *args,
        "-y",
    ]).wait()


def has_correct_codec(video_path: Path) -> bool:
    container = av.open(video_path.as_posix())
    video_stream = container.streams.video[0]
    long_name = video_stream.codec_context.codec.long_name
    container.close()
    return long_name == "MPEG-4 part 2"


def encode_xvid(video_path: Path, quality: int = 10) -> Path:
    encoded_path = video_path.with_suffix(f".xvid.mp4")
    if encoded_path.is_file():
        return encoded_path
    print("Input video has invalid codec. Re-encoding with libxvid…")
    assert 1 <= quality <= 31, f"Quality {quality} is outside the 1-31 range"
    ffmpeg(
        "-i", video_path.as_posix(),
        "-vcodec", "libxvid",
        "-q:v", str(quality),
        "-an",
        encoded_path.as_posix()
    )
    return encoded_path


def get_encoded_path(video_path: Path, quality: int = 10) -> Path:
    if has_correct_codec(video_path):
        return video_path
    return encode_xvid(video_path, quality)


def startfile(path: Path):
    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path.as_posix()])


def get_video_framerate(video_path: Path) -> str:
    data = json.loads(subprocess.check_output([
        "ffprobe",
        "-v", "quiet",
        "-pretty",
        "-print_format", "json",
        "-show_entries", "stream=r_frame_rate",
        "-select_streams", "v:0",
        video_path.as_posix()
    ]))
    return data["streams"][0]["r_frame_rate"]


def drop_xvid_frames(input_path: Path, output_path: Path, quality: int = 10):
    encoded_path = get_encoded_path(input_path, quality)
    temp_path = output_path.with_stem(output_path.stem + "_badpts")
    container = av.open(encoded_path.as_posix())
    output = av.open(temp_path.as_posix(), mode="w")
    video_stream = container.streams.video[0]
    output.add_stream(template=video_stream)
    first_i_frame_written = False
    for packet in container.demux(video_stream):
        if packet.is_keyframe:
            if not first_i_frame_written:
                first_i_frame_written = True
                output.mux(packet)
            else:
                continue
        else:
            output.mux(packet)
    container.close()
    output.close()
    ffmpeg(
        "-fflags", "+genpts",
        "-r", get_video_framerate(input_path),
        "-i", temp_path.as_posix(),
        output_path.as_posix())
    os.remove(temp_path.as_posix())
    startfile(output_path)
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument("-q", "--quality", type=int, default=10,
        help="quality between 1 (highest) to 31 (lowest)")
    args = parser.parse_args()
    drop_xvid_frames(
        Path(args.input_path),
        Path(args.output_path),
        args.quality)


if __name__ == "__main__":
    main()
