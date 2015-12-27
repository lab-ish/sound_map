# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
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
    sig = signal_process.SignalProcess(data.left, data.right)
    sound_map = sig()

    # サウンドマップはindex番号になっているので時間差に変換
    sound_map = sound_map * 1e3 / data.sample_rate

    # ファイルへの書き出し
    index = np.arange(0, len(sound_map))
    timebox = data.sample_timelen * sig.shift * index
    save_data = np.c_[index, timebox, sound_map]
    np.savetxt("sound_map.dat", save_data,
               fmt=["%d", "%g", "%g"],
               delimiter="\t")

    del data
    del sig
