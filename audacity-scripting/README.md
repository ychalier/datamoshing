# Audacity Script

Frame by frame datamoshing relying on Audacity.

## Getting Started

### Prerequisites

You'll need a working installation of [Python 3](https://www.python.org/), and [FFmpeg](https://ffmpeg.org/). Make sure they are in PATH.

You'll also need [Audacity](https://www.audacityteam.org/), and to enable the [mod-script-pipe] module. According to [the documentation](https://manual.audacityteam.org/man/scripting.html):

1. Run Audacity
2. Go into **Edit** > **Preferences** > **Modules**
3. Choose **mod-script-pipe** (which should show **New**) and change that to **Enabled**.
4. Restart Audacity
5. Check that it now does show **Enabled**.

### Installation

Download or clone this repository:

```console
git clone https://github.com/ychalier/datamoshing.git
cd datamoshing/audacity-script/
```

Install the requirements:

```console
pip -m install requirements.txt
```

### Usage

1. Run Audacity
2. Run the [audacity.py](audacity.py) script with the following parameters:
   ```console
   python audacity.py <input-video> <input-filter> <output-video>
   ```

The input filter is a preset text file for the *Filter Curve* effect in Audacity. You'll find some in the [filters](filters) folder. You can create one by running Audacity, opening the *Filter Curve* effect, messing around with the EQ line, and exporting it as a preset .txt file.

## Examples

This grid shows examples for several filter presets.

![](grid.gif)

## References

- [mod-script-pipe documentation](https://manual.audacityteam.org/man/scripting.html)
- [mod-script-pipe test files](https://github.com/audacity/audacity/blob/master/au3/scripts/piped-work/) (location in docs is deprecated)
- [Audacity Scripting Reference](https://manual.audacityteam.org/man/scripting_reference.html)
- [OSError: [Errno 22] Invalid argument](https://forum.audacityteam.org/t/audacity-pipe-python-errno-22/57799/8) (grrr 🥸)