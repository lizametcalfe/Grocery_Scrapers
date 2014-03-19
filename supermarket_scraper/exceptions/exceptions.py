# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:15:41 2014

@author: onsbigdata
"""


class TescoSpiderError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class WaitroseSpiderError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class SpiderError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
