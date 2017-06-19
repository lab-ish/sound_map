.. -*- coding: utf-8; -*-

============================================
 ITSプロジェクト向けSound Map描画プログラム
============================================

音声ファイルの左右音声の類似性をGeneralized Cross-Correlationを使って判断するプログラム。

Required Libraries
==================

* wave
* numpy
* scipy

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
拡張Sound mapデータはwavファイルの拡張子 ``_enhanced.dat`` に変更したものに書き出される。

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

注意事項
========

24-bitのwaveファイルを処理する場合、そのままでは読み込めず変換を行う必要があるためにとても遅い。
可能な限り16-bitなどに変換してから入力すること。

Copyright, License
==================

Copyright (c) 2015-2016, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.**
