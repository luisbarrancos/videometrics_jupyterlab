# JupyterLab video quality assessment metrics notebooks

## What's this?

An exploration of video encoders for generative, procedural art content and computer graphics, since most content presents challenges to default parameter sets. Notably, high frequency content, saturated colors encompassing the majority of the color gamut defined by the sRGB or ITU-R BT.709 RGB primaries.
Erratic, unpredictable motion that poses challenges to motion estimation and compensation algorithms.
Placement of high frequency details in light areas, where encoder quantization is sure to discard them if the settings are aggressive.

## Video Quality Assessment Metrics

Mostly Structure Similarity Index and its Multi-Scale variant.
NetFlix's [Video Multimethod Assessment Fusion](https://github.com/Netflix/vmaf) (aka VMAF) with [FFMPEG](https://ffmpeg.org/), Peak Signal to Noise Ratio or PSNR and Video Information Fidelity or VIF:

## Requirements

You need Python 3.8.10+, a virtual environment is ideal, and install the Python dependencies via the presented [requirements.txt](https://github.com/luisbarrancos/videometrics_jupyterlab/blob/master/requirements.txt) file.

You also need FFMPEG, preferably a modern version. These notebooks were done on Ubuntu 20.04 LTS, but the FFMPEG version used was version 4.4 built from [their github repository](https://github.com/FFmpeg/FFmpeg)

## License

[GNU GPLv3 License](https://github.com/luisbarrancos/videometrics_jupyterlab/blob/master/LICENSE.md).


