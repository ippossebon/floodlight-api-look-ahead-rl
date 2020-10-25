import sys

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.node import Node
from mininet.topolib import TreeTopo
from mininet.util import waitListening

class MastersSwitchTopo(Topo):
    def build(self):
        s1 = self.addSwitch('S1', mac="00:00:00:00:00:01", protocols='OpenFlow13')
        s2 = self.addSwitch('S2', mac="00:00:00:00:00:02", protocols='OpenFlow13')
        s3 = self.addSwitch('S3', mac="00:00:00:00:00:03", protocols='OpenFlow13')
        s4 = self.addSwitch('S4', mac="00:00:00:00:00:04", protocols='OpenFlow13')
        s5 = self.addSwitch('S5', mac="00:00:00:00:00:05", protocols='OpenFlow13')

        h1 = self.addHost('H1', mac="00:00:00:00:00:11", ip="10.0.0.1/24")
        h2 = self.addHost('H2', mac="00:00:00:00:00:12", ip="10.0.0.2/24")
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

def connectToRootNS( network, switch, ip, routes ):
    """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      routes: host networks to route to"""
    # Create a node in root namespace and link to switch 0
    root = Node( 'root', inNamespace=False )
    intf = network.addLink( root, switch ).intf1
    root.setIP( ip, intf=intf )
    # Start network that now includes link to root namespace
    network.start()
    # Add routes from root ns to hosts
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )

def sshd( network, cmd='/usr/sbin/sshd', opts='-D',
          ip='10.123.123.1/32', routes=None, switch=None ):
    """Start a network, connect it to root ns, and run sshd on all hosts.
       ip: root-eth0 IP address in root namespace (10.123.123.1/32)
       routes: Mininet host networks to route to (10.0/24)
       switch: Mininet switch to connect to root namespace (s1)"""
    if not switch:
        switch = network[ 's1' ]  # switch to use
    if not routes:
        routes = [ '10.0.0.0/24' ]
    connectToRootNS( network, switch, ip, routes )
    for host in network.hosts:
        host.cmd( cmd + ' ' + opts + '&' )
    info( "*** Waiting for ssh daemons to start\n" )
    for server in network.hosts:
        waitListening( server=server, port=22, timeout=5 )

    info( "\n*** Hosts are running sshd at the following addresses:\n" )
    for host in network.hosts:
        info( host.name, host.IP(), '\n' )
    info( "\n*** Type 'exit' or control-D to shut down network\n" )
    CLI( network )
    for host in network.hosts:
        host.cmd( 'kill %' + cmd )
    network.stop()

if __name__ == '__main__':
    lg.setLogLevel('info')

    topo = MastersSwitchTopo()
    c1 = RemoteController('c1', ip='192.168.68.250', port=6653) #usando Floodlight
    net = Mininet(topo=topo, controller=c1)

    # get sshd args from the command line or use default args
    # useDNS=no -u0 to avoid reverse DNS lookup timeout
    argvopts = ' '.join( sys.argv[ 1: ] ) if len( sys.argv ) > 1 else (
        '-D -o UseDNS=no -u0' )
    sshd( net, opts=argvopts )
