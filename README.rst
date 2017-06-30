.. -*- coding: utf-8; -*-

============================================
 ITSプロジェクト向けSound Map描画プログラム
============================================

音声ファイルの左右音声の類似性をGeneralized Cross-Correlationを使って判断するプログラム。

Required Libraries
==================

* wave
* numpy
* pandas
* scipy
* scikit-learn

  * for noise reduction

Usage
=====

基本的な使い方
--------------

``python main.py <wavefile>`` のように音声のwavファイルを指定して実行する。
Sound mapデータはwavファイルの拡張子を ``.dat`` に変更したものに書き出される。
出力先を変更したい場合は出力先ファイル名を指定する。

.. code-block:: bash

   % python main.py <wavefile> [soundmap_out]

拡張Sound mapを得る場合は ``main-enhanced.py`` を用いる。
拡張Sound mapデータはwavファイルの拡張子を ``_enhanced.dat`` に変更したものに書き出される。

ノイズ低減型の場合は学習データを別途用意しておく必要がある（現在は ``noise_reduction.py`` を用いて手動で作成してファイルに保存しておく）。
以下のようにPCA、logistic regressionの学習ファイルを指定して実行する。

.. code-block:: bash

   % python main-enhanced-nr.py [-p <pca.pkl>] [-l <lr.pkl>] <wavefile>

``-p`` 、 ``-l`` による指定が無い場合はカレントディレクトリの ``pca.pkl`` 、 ``lr.pkl`` が使用される。
Sound mapデータはwavファイルの拡張子を ``_enhanced_nr.dat`` に変更したものに書き出される。
変更したい場合は ``-o`` オプションを使用する。

GCC結果のグラフ化
-----------------

GCC結果をグラフ化するためには ``plotting.py`` を使用する。

.. code-block:: bash

   % python plotting.py <wavefile>

データをどの位置をグラフ化するかは ``offset`` で指定する。
``offset`` はウィンドウに区切ったデータの何番目を使うかであり、デフォルトは0である。
複数の ``offset`` を指定するとそれぞれのプロットを出力する。

.. code-block:: bash

   % python plotting.py <wavefile> [offset]

1つの図に複数のプロットを描く場合には ``-s`` オプションを指定する。

.. code-block:: bash

   % python plotting.py -s <wavefile> [offset1] [offset2] ...

真値ファイルの作成補助
======================

``srt_to_truth.py`` を用いればSubRip（.srt）形式の字幕から真値ファイルを作成することができる。
字幕の形式は以下の通りとすること。

* 字幕の開始時刻: 車両がマイクの真ん中を通過した時刻。
* 字幕の終了時刻: 車両が画面から出て行った時刻。現在は使用していない。
* 字幕: 方向（L2RまたはR2L） 半角スペース 車両タイプ（normal, truck, bus, van, hvなど）

  * タイプとしてbicycleも入れられるけど、真値ファイルに出力はされない。

このような形式の字幕ファイルを使用し、以下のように実行する。

.. code-block:: bash

   % python srt_to_truth.py output_truth.dat input.srt

注意事項
========

24-bitのwaveファイルを処理する場合、そのままでは読み込めず変換を行う必要があるためにとても遅い。
可能な限り16-bitなどに変換してから入力すること。

Copyright, License
==================

Copyright (c) 2015-2017, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.**
