import os
import shutil
import argparse
import subprocess
import cv2
import numpy
import tqdm
import PIL.Image


def transfer_optical_flow(video_path, image_path, frame_folder=".frames"):
    if os.path.isdir(frame_folder):
        shutil.rmtree(frame_folder)
    os.makedirs(frame_folder)
    video_capture = cv2.VideoCapture(video_path)
    _, video_first_frame = video_capture.read()
    prev_gray = cv2.cvtColor(video_first_frame, cv2.COLOR_BGR2GRAY)
    reference_frame = PIL.Image.open(image_path)
    frame_index = 0
    reference_frame.save(os.path.join(
        frame_folder,
        "%06d.jpg" % frame_index
    ))
    image_frame = numpy.array(reference_frame)
    height, width, depth = image_frame.shape
    framerate = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm.tqdm(
        unit="frame",
        total=frame_count,
        desc="Computing optical flow"
    )
    base = numpy.zeros(height * width * depth, dtype=int)
    for l in range(height * width * depth):
        base[l] = l
    while video_capture.isOpened():
        pbar.update()
        frame_index += 1
        _, video_frame = video_capture.read()
        if video_frame is None:
            break
        gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            prev=prev_gray,
            next=gray,
            flow=None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2, 
            flags=0
        ).astype(int)
        flow_flat = numpy.repeat(
            flow[:, :, 1] * width * depth + flow[:, :, 0] * depth,
            depth
        )
        numpy.put(image_frame, base + flow_flat, image_frame.flat, mode="wrap")
        PIL.Image.fromarray(image_frame).save(os.path.join(
            frame_folder,
            "%06d.jpg" % frame_index
        ))
        prev_gray = gray
    pbar.close()
    video_capture.release()
    return framerate


def create_output_video(frame_folder, framerate, output_path=".frames"):
    subprocess.Popen([
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-stats",
        "-hide_banner",
        "-framerate",
        "%.2f" % framerate,
        "-i",
        os.path.join(frame_folder, "%06d.jpg"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        output_path,
        "-y"
    ]).wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video_path", type=str)
    parser.add_argument("image_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument("-f", "--frame-folder", type=str, default=".frames")
    args = parser.parse_args()
    framerate = transfer_optical_flow(
        args.video_path,
        args.image_path,
        args.frame_folder
    )
    create_output_video(
        args.frame_folder,
        framerate,
        args.output_path
    )


if __name__ == "__main__":
    main()