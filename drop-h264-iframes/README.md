# Drop h264 I-Frames

Removes every reference frames from a video, except the first one.

## Getting Started

### Prerequisites

You'll need a working installation of [Python 3](https://www.python.org/), and [FFmpeg](https://ffmpeg.org/). Make sure they are in PATH.

### Installation

Download or clone this repository:

```console
git clone https://github.com/ychalier/datamoshing.git
cd datamoshing/drop-h264-iframes/
```

Install the requirements:

```console
pip -m install requirements.txt
```

### Basic usage

Simply execute the main script:

```console
python drop_h264_iframes.py full <source-video> <output-video>
```

## Usage

Source and output videos can be of any type, as they will be converted to h264, using FFmpeg, during the process.

You can pass different actions strings to perform different things:

Action | Description
------ | -----------
`preprocess` | Convert the source video to h264 and analyse its NAL units
`rebuild` | Rebuild a video from the h264 source and the NAL units analysis
`full` | Pipeline doing `preprocess` and `rebuild`
`split` | Analyse the NAL units of a h264 video
`probe` | Use FFprobe to analyse frames of a video

### Arguments

You can pass FFmpeg compression arguments that will be applied during conversion to h264. They will impact the result of the datamoshing.

Argument | Default | Description
-------- | ------- | -----------
`--sc-threshold` | `40` | Scenecut detection threshold
`--g` | `250` | Maximum frames between two I-Frames
`--keyint-min` | `25` | Minimum frames between two I-Frames
`--bf` | `0` | Maximum frames between two B-Frames
`--profile` | `main` | Encoding profile
`--level` | `4.0` | Quality level
`--crf` | `23` | Balance between quality and compression

### Tips

For a good effect, you may want to concatenate videos clips together. This can be done using FFmpeg.

1. Create a text file listing the clips to concatenate:
    ```text
    file 'first.mp4'
    file 'second.mp4'
    file 'third.mp4'
    ```
2. Execute the following command:
    ```console
    ffmpeg -f concat -safe 0 -i .\list.txt -c copy output.mp4
    ```

There's more information on [FFmpeg's documentation](https://trac.ffmpeg.org/wiki/Concatenate).

## Example

[![](https://i.imgur.com/hCxqsB0.jpg?1)](https://i.imgur.com/bOHT26q.mp4)

I wrote some details [on my blog](https://chalier.fr/blog/datamoshing#droppingreferenceframes).

## Known Issues

The resulting video may stutter if too many frames are dropped. It it less noticeable with high FPS videos. Unless I get to time travel, I will probably not address it.
