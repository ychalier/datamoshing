# Optical Flow Transfer

Transfer optical flow from one video to an image.

## Getting Started

### Prerequisites

You'll need a working installation of [Python 3](https://www.python.org/), and [FFmpeg](https://ffmpeg.org/). Make sure they are in PATH.

### Installation

Download or clone this repository:

```console
git clone https://github.com/ychalier/datamoshing.git
cd datamoshing/optical-flow-transfer/
```

Install the requirements:

```console
pip -m install requirements.txt
```

## Usage

Simply execute the main script:

```console
python optical_flow_transfer.py <source-video> <source-image> <output-video>
```

## Example

[![](example.gif)](https://drive.chalier.fr/protected/datamoshing/optical-flow-transfer-output.mp4)

I wrote some details [on my blog](https://chalier.fr/blog/datamoshing#opticalflowtransfer).

## Demo

Here is a [web demonstration](www/) where you may try different video sources (such as the webcam) and image sources to perform optical flow transfer.