# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2024, Shigemi ISHIDA
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import sys
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression as LR

#======================================================================
class NoiseReduction():
    def __init__(self, data, div, n_comp=None):
        self.data   = data              # 真値・音声格納のTrueDataオブジェクト
        self.div    = div               # 交差検定の分割数
        self.n_comp = n_comp            # PCAの成分数
        return

    #--------------------------------------------------
    # 全データでcross-validation
    def cross_validation(self, wo_pca=False, pca_all=True):
        results = pd.DataFrame(columns=('tp', 'fn', 'fp', 'tn',
                                        'accuracy', 'precision', 'recall', 'f_measure',
                                        'train_len', 'test_len'))
        test_func = self.pca_lr_test
        if wo_pca:
            test_func = self.lr_test

        for cnt in range(self.div):
            results = results.append(
                pd.Series(test_func(cnt, pca_all),
                          index=('tp', 'fn', 'fp', 'tn',
                                 'accuracy', 'precision', 'recall', 'f_measure',
                                 'train_len', 'test_len')),
                ignore_index=True)

        return results

    #--------------------------------------------------
    # pca_allパラメータは不要だが、pca_lr_testと共通の引数とするために受け取る
    def lr_test(self, train_idx, pca_all=None):
        # cross-validationのindex番号が範囲を超えているときは評価不能
        if train_idx is not None and (train_idx >= self.div or train_idx < 0):
            return False

        idx = range(self.div)

        # 学習用のデータを抽出
        train_data, true_false, train_len = self.data.get_partial_data(idx.pop(train_idx), self.div)
        if train_len is None:
            return False

        # LR学習
        self.lr_train(train_data, true_false)

        # テストデータを連結
        test_data = np.empty([0, train_data.shape[1]])
        true_val  = np.empty(0, dtype='int8')
        test_len  = 0
        for cnt in idx:
            x = self.data.get_partial_data(cnt, self.div)
            if x[0] is not None:
                test_data = np.r_[test_data, x[0]]
                true_val  = np.append(true_val, x[1])
                test_len += x[2]

        # Logistic regression
        #   左列: 推定値、右列: 真値
        results = np.c_[self.lr.predict(test_data), true_val]

        # true positive, false negative, false positive, true negativeの数
        tp = len((results[:,0] & results[:,1] ==  1).nonzero()[0])  # 11
        fn = len((results[:,0] - results[:,1] == -1).nonzero()[0])  # 01
        fp = len((results[:,0] - results[:,1] ==  1).nonzero()[0])  # 10
        tn = len((results[:,0] | results[:,1] ==  0).nonzero()[0])  # 00
        # accuracy, precision, recall, f-measure
        accuracy  = 1.0*(tp+tn)/(tp+fp+fn+tn)
        if tp == 0:
            precision = 0
            recall    = 0
            f_measure = 0
        else:
            precision = 1.0*tp/(tp+fp)
            recall    = 1.0*tp/(tp+fn)
            f_measure = 2.0*precision*recall/(precision+recall)

        return [tp, fn, fp, tn,
                accuracy, precision, recall, f_measure,
                train_len, test_len]

    #--------------------------------------------------
    # cross-validationのindex番号を指定して評価
    def pca_lr_test(self, train_idx, pca_all=True):
        # cross-validationのindex番号が範囲を超えているときは評価不能
        if train_idx is not None and (train_idx >= self.div or train_idx < 0):
            return False

        idx = range(self.div)

        # 学習用のデータを抽出
        train_data, true_false, train_len = self.data.get_partial_data(idx.pop(train_idx), self.div)
        if not train_len:
            return False

        # 全データでPCA学習する？
        if pca_all:
            # PCAの主成分推定
            pca = self.pca_train(train_data)
            # LR学習
            self.lr_train(pca, true_false)
        else:
            # PCAの主成分推定
            true_pca = self.pca_train(train_data[(true_false == 1),:])
            # LR学習用に非通過時のデータをPCA
            false_pca = self.pca_apply(train_data[(true_false == 0),:])
            # LR学習
            self.lr_train(np.r_[true_pca, false_pca], true_false)

        # テストデータを連結
        test_data = np.empty([0, train_data.shape[1]])
        true_val  = np.empty(0, dtype='int8')
        test_len  = 0
        for cnt in idx:
            x = self.data.get_partial_data(cnt, self.div)
            if x[0] is not None:
                test_data = np.r_[test_data, x[0]]
                true_val  = np.append(true_val, x[1])
                test_len += x[2]

        test_pca = self.pca_apply(test_data)

        # Logistic regression
        #   左列: 推定値、右列: 真値
        results = np.c_[self.lr.predict(test_pca), true_val]

        # true positive, false negative, false positive, true negativeの数
        tp = len((results[:,0] & results[:,1] ==  1).nonzero()[0])  # 11
        fn = len((results[:,0] - results[:,1] == -1).nonzero()[0])  # 01
        fp = len((results[:,0] - results[:,1] ==  1).nonzero()[0])  # 10
        tn = len((results[:,0] | results[:,1] ==  0).nonzero()[0])  # 00
        # accuracy, precision, recall, f-measure
        accuracy  = 1.0*(tp+tn)/(tp+fp+fn+tn)
        precision = 1.0*tp/(tp+fp)
        recall    = 1.0*tp/(tp+fn)
        f_measure = 2.0*precision*recall/(precision+recall)

        return [tp, fn, fp, tn,
                accuracy, precision, recall, f_measure,
                train_len, test_len]

    #--------------------------------------------------
    # Logistic regressionの学習
    #   真値ファイルをあらかじめ読み込んでおくこと
    def lr_train(self, train_data, true_false, savefile=None):
        # LR学習
        self.lr = LR(C=1, solver='lbfgs', max_iter=100)
        self.lr.fit(train_data, true_false)

        # 出力先が指定されているならばファイルに保存
        if savefile is not None:
            joblib.dump(self.lr, savefile)

        return True

    #--------------------------------------------------
    def pca_apply(self, data):
        # 単一データの場合は変換して渡す
        if len(data.shape) == 1:
            return self.pca.transform(data.reshape(1,-1))
        # そうでない場合はそのまま渡す
        return self.pca.transform(data)

    #--------------------------------------------------
    def pca_train(self, train_data, savefile=None):
        # 学習
        self.pca = PCA(n_components=self.n_comp)
        transformed = self.pca.fit_transform(train_data)

        # 出力先が指定されているならばファイルに保存
        if savefile is not None:
            joblib.dump(self.pca, savefile)

        return transformed

    #--------------------------------------------------
    def pca_load(self, pca_file):
        self.pca = joblib.load(pca_file)
        self.n_comp = self.pca.n_components_
        return

    #--------------------------------------------------
    def lr_load(self, lr_file):
        self.lr = joblib.load(lr_file)
        return

    #--------------------------------------------------
    def __del__(self):
        return
