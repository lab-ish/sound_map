.. -*- coding: utf-8; -*-

============================================
 ITSプロジェクト向けSound Map描画プログラム
============================================

音声ファイルの左右音声の類似性をGeneralized Cross-Correlationを使って判断し、sound mapデータを得るプログラム。

Required Libraries
==================

* wave
* numpy
* pandas
* scipy
* scikit-learn

  * ノイズ低減型の場合のみ

ノート
======

**本プログラムはwavファイルの情報をきちんと解析しているわけではない。**
このため、以下の形式のwavファイルを用意することを推奨する。

* 16bitステレオ
* 48kHzサンプリング
* Linear PCM, リトルエンディアン

Linear PCMの録音を含むMP4動画から音声を抽出するには ``ffmpeg`` を使うと良い。

.. code-block:: bash

   % ffmpeg -i hoge.mp4 -vn -acodec pcm_s16le hoge.wav

Usage
=====

基本的な使い方
--------------

``python main.py <wavefile>`` のように音声のwavファイルを指定して実行する。
Sound mapデータはwavファイルの拡張子を ``.dat`` に変更したものに書き出される。
出力先を変更したい場合は出力先ファイル名を指定する。

.. code-block:: bash

   % python main.py <wavefile> [soundmap_out]

サンプリング周波数48kHz、データ長16bitのステレオwaveファイルを想定して書かれている（ハードコード）ため、違う場合は適宜書き換えること。
なお、 ``main.py`` で使用している ``wave_data.py`` ではdecimation比率を与えるとdecimationしてくれる。

拡張サウンドマップ方式
----------------------

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

AegiSubで作成した字幕ファイル（.ass）から真値ファイルを作成できる。
字幕の形式は以下の通りとすること。

* 字幕の開始時刻: 車両がマイクの真ん中を通過した時刻。
* 字幕の終了時刻: 車両が画面から出て行った時刻（現在は未使用）
* 字幕: 方向（L2RまたはR2L） 半角スペース 車両タイプ（normal, truck, bus, van, hvなど）

.. code-block:: text

   L2R normal

このような形式の字幕ファイルを使用し、以下のように実行する。

.. code-block:: bash

   % python ass_to_truth.py output_truth.dat input.ass

注意事項
========

24-bitのwaveファイルを処理する場合、そのままでは読み込めず変換を行う必要があるためにとても遅い。
可能な限り16-bitなどに変換してから入力すること。

Our Papers
==========

- M. Uchino, B. Dawton, Y. Hori, S. Ishida, S. Tagashira, Y. Arakawa, and A. Fukuda
  Initial Design of Two-Stage Acoustic Vehicle Detection System for High Traffic Roads
  International Workshop on Pervasive Computing for Vehicular Systems (PerVehicle), in conjunction with IEEE International Conference on Pervasive Computing and Communications (PerCom), Austin, TX, pp.590-595, Mar 2020.
  https://doi.org/10.1109/PerComWorkshops48775.2020.9156248
- S. Ishida, M. Uchino, C. Li, S. Tagashira, and A. Fukuda
  Design of Acoustic Vehicle Detector with Steady-Noise Suppression
  IEEE International Conference on Intelligent Transportation Systems (ITSC), Auckland, New Zealand, pp.2848-2853, Oct 2019.
  https://doi.org/10.1109/ITSC.2019.8917289
- M. Uchino, S. Ishida, K. Kubo, S. Tagashira, and A. Fukuda
  Initial Design of Acoustic Vehicle Detector with Wind Noise Suppressor
  International Workshop on Pervasive Computing for Vehicular Systems (PerVehicle), in conjunction with IEEE International Conference on Pervasive Computing and Communications (PerCom), Kyoto, Japan, pp.814-819, Mar 2019.
  https://doi.org/10.1109/PERCOMW.2019.8730822
- 石田 繁巳, 梶村 順平, 内野 雅人, 田頭 茂明, 福田 晃
  路側設置マイクロフォンを用いた逐次検出型車両検出システム
  情報処理学会論文誌, vol.60, no.1, pp.76-86, Jan 2019.
  http://id.nii.ac.jp/1001/00193796/
- S. Ishida, J. Kajimura, M. Uchino, S. Tagashira, and A. Fukuda
  SAVeD: Acoustic Vehicle Detector with Speed Estimation capable of Sequential Vehicle Detection
  IEEE International Conference on Intelligent Transportation Systems (ITSC), Maui, HI, pp.906-912, Nov 2018.
  https://doi.org/10.1109/ITSC.2018.8569727
- 石田 繁巳, 三村 晃平, 劉 嵩, 田頭 茂明, 福田 晃
  路側設置マイクロフォンによる車両カウントシステム
  情報処理学会論文誌, vol.58, no.1, pp.89-98, Jan 2017.

Copyright, License
==================

This software is released under the BSD 3-clause license. See `LICENSE.txt`.

Copyright (c) 2015-2024, Shigemi ISHIDA

このレポジトリのコードを参照したり使用したりする場合は、関連論文をご参照の上、関連する論文を引用くださいますようお願いいたします。
