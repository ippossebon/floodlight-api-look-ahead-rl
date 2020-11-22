#!/usr/bin/python
# -*- coding: utf-8 -*-


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.node import OVSSwitch, Controller, RemoteController

class MastersSwitchTopo(Topo):
    def build(self):
        s1 = self.addSwitch('S1', protocols='OpenFlow13')
        s2 = self.addSwitch('S2', protocols='OpenFlow13')
        s3 = self.addSwitch('S3', protocols='OpenFlow13')
        s4 = self.addSwitch('S4', protocols='OpenFlow13')
        s5 = self.addSwitch('S5', protocols='OpenFlow13')
        s6 = self.addSwitch('S6', protocols='OpenFlow13')
        s7 = self.addSwitch('S7', protocols='OpenFlow13')
        s8 = self.addSwitch('S8', protocols='OpenFlow13')
        s9 = self.addSwitch('S9', protocols='OpenFlow13')
        s10 = self.addSwitch('S10', protocols='OpenFlow13')

        h1 = self.addHost('H1')
        h2 = self.addHost('H2')


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
            node1 = s1,
            node2 = s7,
            port1 = 4,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )

        self.addLink(
            node1 = s1,
            node2 = s8,
            port1 = 5,
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
            node1 = s2,
            node2 = s6,
            port1 = 5,
            port2 = 2,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )

        self.addLink(
            node1 = s3,
            node2 = s10,
            port1 = 5,
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

        self.addLink(
            node1 = s4,
            node2 = s9,
            port1 = 4,
            port2 = 2,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )


        self.addLink(
            node1 = s5,
            node2 = s6,
            port1 = 3,
            port2 = 3,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )


        self.addLink(
            node1 = s7,
            node2 = s6,
            port1 = 2,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )

        self.addLink(
            node1 = s8,
            node2 = s9,
            port1 = 2,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )

        self.addLink(
            node1 = s9,
            node2 = s10,
            port1 = 3,
            port2 = 1,
            bw=10, # bw = Mbits/seg,
            cls=TCLink
        )

if __name__ == '__main__':
    setLogLevel('info')
    topo = MastersSwitchTopo()
    # c1 = RemoteController('c1', ip='127.0.0.1') #usando RYU
    # c1 = RemoteController('c1', ip='0.0.0.0', port=6653) #usando Floodlight
    c1 = RemoteController('c1', ip='192.168.68.250', port=6653) #usando Floodlight

    net = Mininet(topo=topo, controller=c1)
    net.start()
    #net.pingAll()
    CLI(net)
    net.stop()
