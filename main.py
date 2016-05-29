# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import os
import numpy as np

import wave_data
import signal_process

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile> [soundmap_out]\n" % sys.argv[0])
        quit()

    # 引数処理
    wavefile = sys.argv[1]
    # sound mapデータの出力先のデフォルトはwaveファイルの拡張子を".dat"に変更したもの
    outname = os.path.splitext(wavefile)[0] + '.dat'
    if len(sys.argv) >= 3:
        outname = sys.argv[2]

    # データ読み込み
    data = wave_data.WaveData(wavefile)

    # データ処理
    sig = signal_process.SignalProcess(data.left, data.right)
    sound_map = sig()

    # サウンドマップはindex番号になっているので時間差に変換
    sound_map = sound_map * 1e3 / data.sample_rate

    # ファイルへの書き出し
    if outfile is not None:
        index = np.arange(0, len(sound_map))
        timebox = data.sample_timelen * sig.shift * index
        save_data = np.c_[index, timebox, sound_map]
        np.savetxt(outname, save_data,
                   fmt=["%d", "%g", "%g"],
                   delimiter="\t")

    del data
    del sig
