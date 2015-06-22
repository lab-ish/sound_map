# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.
#

import sys
import numpy as np

import wave_data
import signal_process

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile>\n" % sys.argv[0])
        quit()

    # データ読み込み
    wavefile = sys.argv[1]
    data = wave_data.WaveData(wavefile)

    # データ処理
    sig = signal_process.SignalProcess(data.raw_data[0], data.raw_data[1])
    sound_map = sig()

    # ファイルへの書き出し
    index = np.arange(0, len(sound_map))
    timebox = data.sample_timelen * sig.shift * index
    sound_maptime = sound_map * data.sample_timelen
    save_data = np.c_[index, timebox, sound_map, sound_maptime]
    np.savetxt("sound_map.dat", save_data,
               fmt=["%d", "%g", "%g", "%g"],
               delimiter="\t")

    del data
