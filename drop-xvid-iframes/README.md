# Drop Xvid I-Frames

Removes every reference frames from a video, except the first one.

## Getting Started

### Prerequisites

You'll need a working installation of [Python 3](https://www.python.org/), and [FFmpeg](https://ffmpeg.org/). Make sure they are in PATH.

### Installation

Download or clone this repository:

```console
git clone https://github.com/ychalier/datamoshing.git
cd datamoshing/drop-xvid-iframes/
```

Install the requirements:

```console
pip -m install requirements.txt
```

### Basic usage

Simply execute the main script:

```console
python drop_xvid_iframes.py <input-video> <output-video>
```

## Example

[![](example.gif)](https://drive.chalier.fr/protected/datamoshing/xvid.mp4)
