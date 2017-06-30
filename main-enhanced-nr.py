# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import os
import numpy as np

import true_data
import noise_reduction
import esignal_process_nr

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile> [soundmap_out]\n" % sys.argv[0])
        quit()

    # 引数処理
    wavefile = sys.argv[1]
    # sound mapデータの出力先のデフォルトはwaveファイルの最後を'_enhanced_nr.dat'としたもの
    outname = os.path.splitext(wavefile)[0] + '_enhanced_nr.dat'
    if len(sys.argv) >= 3:
        outname = sys.argv[2]

    # データ読み込み
    #   true_dataファイルのデフォルトはwaveファイルベース+'_truth.dat'
    base_name = os.path.splitext(wavefile)[0]
    base_dir  = os.path.dirname(base_name)
    true_file = base_name + '_truth.dat'
    data = true_data.TrueData(true_file, wavefile)

    # データ処理
    nr = noise_reduction.NoiseReduction(data, 6, 17)
    nr.pca_load(base_dir + "/pca.pkl")
    nr.lr_load(base_dir + "/lr.pkl")
    esign = esignal_process_nr.ESignalProcessNr(data.wav.left, data.wav.right, nr, data.samp_rate)
    esound_map_nr = esign()

    # サウンドマップはindex番号になっているので時間差に変換
    esound_map_time_nr = esound_map_nr * 1e3 / data.samp_rate

    # ファイルへの書き出し
    index = np.arange(len(esound_map_nr))
    timebox = 1.0 * index * esign.shift / data.samp_rate
    save_data = np.c_[index, timebox,
                      esound_map_nr, esound_map_time_nr]
    print "Writing output to %s ..." % (outname)
    with open(outname, "w") as f:
        f.write("#index\ttime\tesound_nr_delay\tesound_nr_delay_time\n")
        np.savetxt(f, save_data,
                   fmt=["%d", "%g", "%d", "%g"],
                   delimiter="\t")

    del data
    del esign
    del nr
