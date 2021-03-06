#!/usr/bin/python
# -*- coding: utf-8 -*-


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import OVSSwitch, Controller, RemoteController, Node

import time

class MastersSwitchTopo(Topo):
    def build(self):
        s1 = self.addSwitch('S1', mac="00:00:00:00:00:01", protocols='OpenFlow13')
        s2 = self.addSwitch('S2', mac="00:00:00:00:00:02", protocols='OpenFlow13')
        s3 = self.addSwitch('S3', mac="00:00:00:00:00:03", protocols='OpenFlow13')
        s4 = self.addSwitch('S4', mac="00:00:00:00:00:04", protocols='OpenFlow13')
        s5 = self.addSwitch('S5', mac="00:00:00:00:00:05", protocols='OpenFlow13')

        h1 = self.addHost('H1', mac="00:00:00:00:00:11", ip="10.0.0.1/12")
        h2 = self.addHost('H2', mac="00:00:00:00:00:12", ip="10.0.0.2/12")
        # h3 = self.addHost('H3', mac="00:00:00:00:00:13", ip="10.0.0.3/12")
        # h4 = self.addHost('H4', mac="00:00:00:00:00:14", ip="10.0.0.4/12")


        # Adiciona hosts aos switches
        self.addLink(
            node1 = h1,
 	        node2 = s1,
 	        port1 = 1,
 	        port2 = 1,
            bw=50, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = h2,
 	        node2 = s3,
 	        port1 = 1,
 	        port2 = 1,
            bw=50, # bw = Mbits/seg,
            cls=TCLink
        )

        # Adiciona links entre os switches
        self.addLink(
            node1 = s1,
            node2 = s2,
            port1 = 2,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = s1,
            node2 = s4,
            port1 = 3,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = s2,
            node2 = s4,
            port1 = 2,
            port2 = 2,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = s2,
            node2 = s5,
            port1 = 3,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = s2,
            node2 = s3,
            port1 = 4,
            port2 = 2,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = s4,
            node2 = s3,
            port1 = 3,
            port2 = 3,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )
        self.addLink(
            node1 = s5,
            node2 = s3,
            port1 = 2,
            port2 = 4,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )

if __name__ == '__main__':
    setLogLevel('info')
    topo = MastersSwitchTopo()
    c1 = RemoteController('c1', ip='192.168.68.250', port=6653) #usando Floodlight

    net = Mininet(topo=topo, controller=c1)
    net.start()

    CLI(net)


    # print('\n\nParando a rede...')
    # net.stop()
