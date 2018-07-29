# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#======================================================================
# 引数処理
def arg_parser():
    import argparse
    DEF_RANGE = 3.0
    ap = argparse.ArgumentParser()
    ap.add_argument("soundmap", type=str, action="store",
                    help="soundmap file",
                    )
    ap.add_argument("fnfile", type=str, action="store",
                    help="FN file",
                    )
    ap.add_argument("-p", "--plotbase", type=str, action="store",
                    help="plot output filename base",
                    default="",
                    )
    ap.add_argument("-r", "--range", type=float, action="store",
                    help="Time range of plot, default=%.2f" % DEF_RANGE,
                    default=DEF_RANGE,
                    )
    return ap

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    soundmap = np.loadtxt(args.soundmap, usecols=[1,3])
    fndata   = pd.read_csv(args.fnfile, index_col=0)

    fndata["start"] = fndata.true_pass - args.range/2
    fndata["end"]   = fndata.true_pass + args.range/2
    start_end = np.array(fndata[["start", "end"]])

    for i in range(start_end.shape[0]):
        start = start_end[i,0]
        end   = start_end[i,1]
        plotout = args.plotbase + "fn_%.2f.eps" % (start + args.range/2)

        fig = plt.figure()
        #------------------------------
        plt.rcParams['font.family'] = 'Times New Roman' # 全体のフォント
        plt.rcParams['font.size'] = 18                # フォントサイズ
        plt.rcParams['axes.linewidth'] = 1            # 軸の太さ
        fig.subplots_adjust(bottom = 0.15)            # 下の余白を増やす
        # EPS出力のためのおまじない
        plt.rcParams['ps.useafm'] = True
        plt.rcParams['pdf.use14corefonts'] = True
        plt.rcParams['text.usetex'] = True
        #------------------------------
        plt.xlim([start,end])
        plt.ylim([-1.55,1.55])
        plt.xlabel("Time [s]")
        plt.ylabel("Sound Delay [ms]")
        plt.plot(soundmap[:,0], soundmap[:,1], '.')
        plt.savefig(plotout)
        plt.close()
