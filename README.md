# Sound Mapping for Vehicle Sensing

> Calculate generalized cross-correlation (GCC) on stereo sound signals to derive sound map

## Requirements

This software requires packages below:

* wave
* numpy
* pandas
* scipy
* scikit-learn
  * only when you perform noise reduction

## Assumptions

We assume wave file with the format below:
* 16bit stereo
* sampled at 48kHz
* Linear PCM, little endian

If you have an MP4 with a linear-PCM sound track, you can use ffmpeg to extract the sound track:
```bash
ffmpeg -i hoge.mp4 -vn -acodec pcm_s16le hoge.wav
```

## Usage

### Basic Usage

Execute main.py with path to a wave file.
```bash
python main.py <wavefile> [soundmap_out]
```
By default, sound map data is extracted to the `.dat` file.
You can change the output file name with `-o` option.

Please refer to the assumptions section.
If you are using a different format wave file, some more implementation in `wave_data.py` might be required.

### Extended Sound Mapping

With `main-enhanced.py`, you can derive extended sound maps.
By default, the output is named as `_enhanced.dat`.

For noise reduction, you can execute noise-reduction version of sound mapping by:
```bash
python main-enhanced-nr.py [-p <pca.pkl>] [-l <lr.pkl>] <wavefile>
```
where `pca.pkl` and `lr.pkl` are PCA and logistic regression trained data, respectively.

If you omit `-p` and  `-l` options, `pca.pkl` and `lr.pkl` in the current directory are used.

`pca.pkl` and `lr.pkl` needs to be prepared prior to using `main-enhanced-nr.py`.
You can use `noise_reduction.py` to generate these files.

### GCC Plotting

To obtain the GCC result plot, you can use plotting.py.

```bash
python plotting.py <wavefile>
```

Use `offset` to shift the plotting window.
The `offset` specifies the window to plot.

```bash
python plotting.py <wavefile> [offset]
```

If you want multiple GCC results on a single plot, use `-s` option.
```bash
python plotting.py -s <wavefile> [offset1] [offset2] ...
```

## Ground Truth Labeling Support

From a AegiSub subtitle file, we can create a ground-truth vehicle passing data file.
Subtitles should be formatted as:
- Start of the subtitle: vehicle passing right in front of microphones
- End of the subtitle: vehicle passes away from the view of ground truth camera (currently unused)
- Subtitle text: <L2R|R2L> <normal|truck|bus|van|hv>, which indicates the direction and vehicle type.

You can now derive a ground truth file.
```bash
python ass_to_truth.py output_truth.dat input.ass
```

## CAUTION

24-bit wave file results in TOO LONG processing.
We highly recommend to convert 24-bit waves file into 16-bit wave files.

## License

This software is released under the BSD 3-clause license. See `LICENSE.txt`.

* Copyright (c) 2015-2024, Shigemi ISHIDA
