#!/usr/bin/env python

from dingtalk.ding import Ding

ding = Ding()

if __name__ == '__main__':
    ding.send("hello world.")
