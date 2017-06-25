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
import esignal_process

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile> [soundmap_out]\n" % sys.argv[0])
        quit()

    # 引数処理
    wavefile = sys.argv[1]
    # sound mapデータの出力先のデフォルトはwaveファイルの拡張子を".dat"に変更したもの
    outname = os.path.splitext(wavefile)[0] + '_enhanced.dat'
    if len(sys.argv) >= 3:
        outname = sys.argv[2]

    # データ読み込み
    data = wave_data.WaveData(wavefile)

    # データ処理
    sig = signal_process.SignalProcess(data.left, data.right, data.sample_rate)
    esig = esignal_process.ESignalProcess(data.left, data.right, data.sample_rate)
    sound_map  = sig()
    esound_map = esig()

    # サウンドマップはindex番号になっているので時間差に変換
    sound_map_time  =  sound_map * 1e3 / data.sample_rate
    esound_map_time = esound_map * 1e3 / data.sample_rate

    # ファイルへの書き出し
    index = np.arange(0, len(sound_map))
    timebox = data.sample_timelen * sig.shift * index
    save_data = np.c_[index, timebox, sound_map, sound_map_time, esound_map, esound_map_time]
    print "Writing output to %s ..." % (outname),
    with open(outname, "w") as f:
        f.write("#index\ttime\tsound_delay\tsound_delay_time\tesound_delay\tesound_delay_time\n")
        np.savetxt(f, save_data,
                   fmt=["%d", "%g", "%d", "%g", "%d", "%g"],
                   delimiter="\t")
    print "done"

    del data
    del sig
    del esig
