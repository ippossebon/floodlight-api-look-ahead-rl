# -*- coding: utf-8 -*-

class ActiveFlow(object):
    def __init__(self, eth_dst, eth_src, ipv4_dst, ipv4_src, eth_type, in_port):
        self.eth_dst = eth_dst
        self.eth_src = eth_src
        self.ipv4_dst = ipv4_dst
        self.ipv4_src = ipv4_src
        self.eth_type = eth_type # indica o protocolo
        self.in_port = in_port # possivelmente irrelevante
        self.id = self.createId()
        self.features = []
        self.path = []

    def createId(self):
        flow_id = '{eth_dst}-{eth_src}-{in_port}-{eth_type}'.format(
            eth_dst=self.eth_dst,
            eth_src=self.eth_src,
            in_port=self.in_port,
            eth_type=self.eth_type
        )

        return flow_id

    def addFeature(self, feature):
        self.features.append(feature)

    def setPath(self, path):
        self.path = path
