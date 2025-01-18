# Datamoshing

This repository contains Python scripts to perform some datamoshing effects.

For details about how this works and what it does, please see [this blog article](https://chalier.fr/blog/datamoshing).

## Contents

Script | Description
------ | -----------
[Drop h264 I-Frames](drop-h264-iframes/) | Removes every reference frames from a video, except the first one. (poorly works)
[Drop Xvid I-Frames](drop-xvid-iframes/) | Removes every reference frames from a video, except the first one. (works great!)
[Optical Flow Transfer](optical-flow-transfer/) | Transfer optical flow from one media to another. Dedicated repository: [Transflow](https://github.com/ychalier/transflow/).
[Audacity Scripting](audacity-scripting/) | Frame by frame datamoshing relying on Audacity.

## Examples

Here are some videos made using those scripts (click on the thumbnails to see the videos):

Drop h264 I-Frames | Drop Xvid I-Frames | Optical Flow Transfer | Audacity Scripting
------------------ | ------------------ | --------------------- | ------------------
[![](drop-h264-iframes/example.gif)](https://drive.chalier.fr/protected/datamoshing/sunrise-dive.mp4) | [![](drop-xvid-iframes/example.gif)](https://drive.chalier.fr/protected/datamoshing/xvid.mp4) | [![](https://github.com/ychalier/transflow/raw/main/out/ExampleDeer.gif)](https://github.com/ychalier/transflow/raw/main/out/ExampleDeer.mp4) | ![](audacity-scripting/example.gif)

