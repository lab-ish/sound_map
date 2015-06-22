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
    # sound_map = sig(1000000)
    sound_map = sig(10000)

    # 真ん中より先は折り返してマイナスとする
    #   例: 1024点の場合のindex変換
    #      元: 0 1 2 3 ... 510 511  512  513 ... 1022 1023
    #      ↓
    #      後: 0 1 2 3 ... 510 511 -512 -511 ...   -2   -1
    sound_map[(sound_map >= sig.winsize/2)] -= sig.winsize

    # ファイルへの書き出し
    index = np.arange(0, len(sound_map))
    timebox = data.sample_timelen * sig.shift * index
    save_data = np.c_[index, timebox, sound_map]
    np.savetxt("sound_map.dat", save_data,
               fmt=["%d", "%g", "%g"],
               delimiter="\t")

    del data
    del sig
