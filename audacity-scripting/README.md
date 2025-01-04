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

The input filter is a preset text file for built-in effects in Audacity such as *Filter Curve* or *Reverb*. You'll find some in the [filters](filters) folder. You can create one by running Audacity, opening the effect, messing around with the parameters, and exporting it as a preset `.txt` file. Multiple filters can be applied, on multiple lines. Blank lines and lines starting with `#` are ignored. Expressions between braces are evaluated using Python `eval` function, depending on the parameter `t`, the output frame timestamp in seconds (you can write the expression yourself or use tools such as [Lagrange Polynomial Editor](https://chalier.fr/lagrange/) to build larger ones). Here are some examples:

```text
# Echo with variable decay
Echo:Decay="{0.25 * (1 + math.sin(0.5 * t * 6))}" Delay="1"

# Low-pass with variable cut-off
FilterCurve:f0="{10**(2 + math.sin(t * 6.28))}" f1="{10**(2 + math.sin(t * 6.28)) + 20}" FilterLength="8191" InterpolateLin="0" InterpolationMethod="B-spline" v0="-30" v1="0"
```

## Examples

This grid shows examples for several filter presets.

![](grid.gif)

## References

- [mod-script-pipe documentation](https://manual.audacityteam.org/man/scripting.html)
- [mod-script-pipe test files](https://github.com/audacity/audacity/blob/master/au3/scripts/piped-work/) (location in docs is deprecated)
- [Audacity Scripting Reference](https://manual.audacityteam.org/man/scripting_reference.html)
- [OSError: [Errno 22] Invalid argument](https://forum.audacityteam.org/t/audacity-pipe-python-errno-22/57799/8) (grrr 🥸)