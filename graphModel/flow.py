# -*- coding: utf-8 -*-

class Flow(object):
    def __init__(self, id, source, target, bandwidth):
        self.id = id
        self.source = source
        self.target = target
        self.bandwidth = bandwidth
        self.path = []

    def setPath(self, path):
        self.path = path
