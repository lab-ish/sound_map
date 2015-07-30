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

:code:`python main.py <wavefile>` のように音声のwavファイルを指定して実行する。

台数カウントを行う場合は :code:`main.py` の代わりに :code:`main-count.py` を用いる。


注意事項
========

24-bitのwaveファイルを処理する場合はとても遅いです。

* 24-bitはそのままでは読み込めず、変換を行う必要があるため。

Copyright, License
==================

Copyright (c) 2015, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.**
