# -*- coding: utf-8 -*-

class Node(object):
    def __init__(self, id, inetAddress=None, connectedSince=None):
        self.id = id # switchDPID
        self.inetAddress = inetAddress
        self.connectedSince = connectedSince

    def printInfo(self):
        print('* Switch ID = ', self.id)
        print('inetAddress = ', self.inetAddress)
        print('connectedSince = ', self.connectedSince)
