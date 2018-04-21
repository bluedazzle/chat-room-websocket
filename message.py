# coding: utf-8
from __future__ import unicode_literals


class WsMessage(object):
    def __init__(self, raw):
        self.raw = raw
        self.action = ''