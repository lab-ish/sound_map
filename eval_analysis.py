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
import sys

#======================================================================
# 引数処理
def arg_parser():
    import argparse
    DEF_RANGE  = 3.0
    DEF_THRESH = 0.6
    ap = argparse.ArgumentParser()
    ap.add_argument("truth_data", type=str, action="store",
                    help="ground truth data file",
                    )
    ap.add_argument("estimate_data", type=str, action="store",
                    help="estimated data file",
                    )
    ap.add_argument("-r", "--range", type=float, action="store",
                    help="Time range of plot, default=%.2f" % DEF_RANGE,
                    default=DEF_RANGE,
                    )
    ap.add_argument("-t", "--thresh", type=float, action="store",
                    help="Time threshold for matching, default=%.2f" % DEF_THRESH,
                    default=DEF_THRESH,
                    )
    ap.add_argument("-s", "--soundmap", type=str, action="store",
                    help="soundmap file for plotting",
                    default=None,
                    )
    ap.add_argument("--fn_plot", type=str, action="store",
                    help="FN plot output filename base",
                    default=None,
                    )
    ap.add_argument("--fp_plot", type=str, action="store",
                    help="FP plot output filename base",
                    default=None,
                    )
    return ap

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # データを読み込み
    #   真値
    df_tru = pd.read_csv(args.truth_data, delimiter="\t").rename(columns={"#time": "time"})
    #   検出結果
    df_est = pd.read_csv(args.estimate_data).rename(columns={"#time": "time"})

    # 左右方向別に検出判定
    df_tru["match"] = False
    df_est["match"] = False
    df_est["true_time"] = np.nan
    df_est["type"] = ""
    for d in ["L2R", "R2L"]:
        df_est_eval = df_est[df_est.dir == d].copy()
        def find_drop_nearest(x):
            # 検出時刻が最も近いやつを探す
            diff= (df_est_eval.time - x.time).abs().sort_values()
            # 検出時刻が真値通過時刻と近いやつはマッチ
            if diff.iloc[0] < args.thresh:
                df_tru.loc[x.name, "match"] = True
                df_est.loc[diff.head(1).index, "match"] = True
                df_est.loc[diff.head(1).index, "true_time"] = x.time
                df_est.loc[diff.head(1).index, "type"] = x.type
                df_est_eval.drop(index=diff.head(1).index, inplace=True)
        df_tru[df_tru.dir == d].apply(find_drop_nearest, axis=1)

    # 結果をまとめたdataframeを作成
    df_tru["true"] = True
    df_est["detect"] = True
    df_est.rename(columns={"match": "true"}, inplace=True)
    result = pd.concat([df_est, df_tru[df_tru.match == False]], sort=False).sort_values("time").drop(columns="match")
    result.detect = result.detect.fillna(False)

    # 保存
    name = args.estimate_data.split(".")
    base = ".".join(name[0:len(name)-1])
    outname = base + "_est.tsv"
    with open(outname, "w") as f:
        f.write("#")
        result.to_csv(f, sep="\t", index=False)

    # TP, FN, FPはそれぞれ以下の条件を探し出せばOK
    tp = result[(result.true == True) & (result.detect == True)]
    fn = result[(result.true == True) & (result.detect == False)]
    fp = result[(result.true == False) & (result.detect == True)]

    # プロット指定のときはsoundmapファイルが指定されていないとエラー
    if args.fn_plot is not None or args.fp_plot is not None:
        if args.soundmap is None:
            sys.stderr.write("No soundmap file specified for plotting.\n")
            quit()

        # soundmapデータの読み込み
        soundmap = np.loadtxt(args.soundmap, usecols=[1,3])

    def plot_time(df, basename):
        start = df.time - args.range/2
        end   = df.time + args.range/2
        plotout = basename + ("_%.2f_" % df.time) + df.dir + ".eps"
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

    if args.fn_plot is not None:
        fn.apply(plot_time, axis=1, args=[args.fn_plot])

    if args.fp_plot is not None:
        fp.apply(plot_time, axis=1, args=[args.fp_plot])
