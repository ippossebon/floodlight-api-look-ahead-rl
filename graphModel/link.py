# -*- coding: utf-8 -*-

class Link(object):
    def __init__(self, node1, node2, node1_port, node2_port, weight=500):
        self.node1 = node1
        self.node1_port = node1_port
        self.node2 = node2
        self.node2_port = node2_port
        self.weight = weight

    def updateBandwidth(self, new_bandwidth):
        self.weight = new_bandwidth
