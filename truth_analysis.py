# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import pandas as pd
import numpy as np

#======================================================================
class TruthData():
    def __init__(self, truth_file):
        self.infile = truth_file
        # データファイルの読み込み
        self.data = pd.read_csv(self.infile, sep="\t", skiprows=1, header=None,
                                names=["time", "type", "dir"])
        # データを通過時刻で並べ替える
        self.data.sort_values("time", inplace=True)
        return

    #--------------------------------------------------
    def num_simul_successive(self, range=2):
        # 通過時刻を並べ替えた上で差分を取る
        #   通過時刻は1列目
        diff = np.diff(self.data.time)
        # 先頭または最後にinfinityをつけることでデータ数を揃えてからデータフレームに格納
        self.data["diff_prev"] = np.insert(diff, 0, np.inf)
        self.data["diff_next"] = np.append(diff, np.inf)

        #--------------------------------------------------
        ### 連続，同時が混ざっていていいなら以下で十分
        # # diffが2以下のやつのindex番号を取得
        # idx = (self.data.diff_next <= range).nonzero()[0]
        # # index番号の差が1以下の個数（連続して並んでいる個数）
        # d = np.diff(idx)
        # num_successive = len(d[d == 1])
        # # 最終的な連続通過台数は、2以下のdiffの個数*2 - 連続して並んでいる個数
        # self.num_simul = len(idx) * 2 - num_successive
        #--------------------------------------------------

        # 近い車が前か後かを判定
        self.data["closer"] = (self.data.diff_next < self.data.diff_prev)
        self.data.loc[(self.data.closer == False), "closer"] = -1
        self.data.loc[(self.data.closer == True),  "closer"] = 1

        # 近い方との通過時刻差
        self.data["diff_closer"] = self.data[["diff_prev", "diff_next"]].min(axis=1)

        # 近い方の車の進行方向
        self.data["dir_closer"] = self.data.apply(
            lambda x: self.data.loc[x.name+x.closer, "dir"],
            axis=1)

        # 連続，同時通過を抽出
        self.simul_successive = self.data[(self.data.diff_closer <= range)][["time", "type", "dir", "diff_closer", "dir_closer"]]
        # 連続なのか同時なのかを判定（最も近い車の向きで決定）
        self.simul_successive["is_simul"] = self.simul_successive.dir != self.simul_successive.dir_closer

        grp = self.simul_successive[["dir", "is_simul"]].groupby("dir")
        result = (grp.sum().rename(columns={"is_simul": "num_simul"})).astype("int")
        result["num_successive"] = grp.size() - result.num_simul

        # 全体も数えておく
        result["all"] = self.data.groupby("dir").size()

        return result

#======================================================================
# 引数処理
def arg_parser():
    DEFAULT_RANGE = 2
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("truth_file", type=str, action="store",
                    help="truth data TSV file",
                    )
    ap.add_argument("-r", "--range", type=float, action="store",
                    default=DEFAULT_RANGE,
                    help="time length as we regard simultaneous passing",
                    )
    return ap

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    t = TruthData(args.truth_file)
    ret = t.num_simul_successive(args.range)

    print ret
