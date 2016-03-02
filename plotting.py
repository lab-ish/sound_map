# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt

import wave_data
import signal_process

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile> [offset=0]\n" % sys.argv[0])
        quit()
    offset = 0
    if len(sys.argv) >= 3:
        offset = int(sys.argv[2])

    # データ読み込み
    wavefile = sys.argv[1]
    data = wave_data.WaveData(wavefile)

    # データ処理
    sig = signal_process.SignalProcess(data.left, data.right)

    #------------------------------
    # gcc-phatを手動で呼ぶ
    fft_data1 = sig.fft(sig.data1, offset)
    fft_data2 = sig.fft(sig.data2, offset)
    # 帯域の1/8のLPF
    lowpass = np.append(np.append(np.ones(sig.winsize/16),
                                  np.zeros(sig.winsize-sig.winsize/8)),
                                  np.ones(sig.winsize/16))
    fft_data1 = lowpass * fft_data1
    fft_data2 = lowpass * fft_data2
    gcc = sig.gcc(fft_data1, fft_data2)
    # 後半部分を折り返しておく
    gcc_minus = np.array(gcc[sig.winsize/2:len(gcc)])
    gcc[sig.winsize/2:len(gcc)] = np.array(gcc[0:sig.winsize/2])
    gcc[0:sig.winsize/2] = gcc_minus
    gcc = np.real(gcc)

    # gccの横軸はindex番号になっているので時刻を計算しておく
    timebox = np.arange(-sig.winsize/2, sig.winsize/2) * 1e3 / data.sample_rate

    # ファイル名はbasenameを使う（拡張子を変更したものにする）
    outname = os.path.splitext(wavefile)[0] + '.eps'

    # plot
    fig = plt.figure()
    plt.plot(timebox, gcc,
             marker='',
             linestyle='-',
             )
    plt.xlabel("Time $t$ [ms]")
    plt.ylabel("Generalized cross correlation")
    # プロットの調整
    plt.rcParams['font.family'] = 'Times New Roman' # 全体のフォント
    plt.rcParams['font.size'] = 22                  # フォントサイズ
    plt.rcParams['axes.linewidth'] = 1              # 軸の太さ
    fig.subplots_adjust(left=0.15, bottom=0.15)     # 左と下の余白を増やす
    # EPS出力のためのおまじない
    plt.rcParams['ps.useafm'] = True
    plt.rcParams['pdf.use14corefonts'] = True
    plt.rcParams['text.usetex'] = True

    plt.savefig(outname)
