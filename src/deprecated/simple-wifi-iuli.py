#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys

from functools import partial

from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mn_wifi.node import Station
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi


def topology():
    
    privateDirs = [ ( '/var/log', '/tmp/%(name)s/var/log' ),
                    ( '/var/run', '/tmp/%(name)s/var/run' ),
                    ( '/run', '/tmp/%(name)s/run' ),
                      '/var/mn' ]
    station = partial( Station,
                    privateDirs=privateDirs )
    "Create a network."
    net = Mininet_wifi(station=station)

    info("*** Creating nodes\n")
    sta_arg = dict()
    ap_arg = dict()
    if '-v' in sys.argv:
        sta_arg = {'nvif': 2}
    else:
        # isolate_clientes: Client isolation can be used to prevent low-level
        # bridging of frames between associated stations in the BSS.
        # By default, this bridging is allowed.
        # OpenFlow rules are required to allow communication among nodes
        ap_arg = {'client_isolation': True}


    ap_d0 = net.addAccessPoint('ap_d0', protocols='OpenFlow13', ssid="simpletopo", mode="g",
                             channel="5", position='20,20,0', **ap_arg)
    
    ap_h0 = net.addAccessPoint('ap_h0', protocols='OpenFlow13', ssid="simpletopo2", mode="g",
                             channel="11", position='40,20,0', **ap_arg)
    
    ap_v0 = net.addAccessPoint('ap_v0', protocols='OpenFlow13', ssid="simpletopo3", mode="g",
                             channel="11", position='20,40,0', **ap_arg)

    ap_s0 = net.addAccessPoint('ap_s0', protocols='OpenFlow13', ssid="simpletopo4", mode="g",
                             channel="11", position='40,40,0', **ap_arg)

    
    d0 = net.addStation('d0', position='10,10,0', **sta_arg)
    h0 = net.addStation('h0', position='50,10,0', )
    v0 = net.addStation('v0', position='10,50,0', )
    s0 = net.addStation('s0', position='50,50,0', )
    
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    info("*** Configuring propagation model\n")
    net.setPropagationModel(model='logDistance', exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(ap_d0, ap_h0)
    net.addLink(ap_h0, ap_v0)
    net.addLink(ap_v0, ap_s0)

    net.addLink(d0, ap_d0)
    net.addLink(h0, ap_h0)
    net.addLink(v0, ap_v0)
    net.addLink(s0, ap_s0)

    if '-p' not in sys.argv:
        net.plotGraph(max_x=100, max_y=100)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap_d0.start([c0])
    ap_h0.start([c0])
    ap_v0.start([c0])
    ap_s0.start([c0])

    if '-v' not in sys.argv:
        ap_d0.cmd('ovs-ofctl add-flow ap_d0 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
        ap_d0.cmd('ovs-ofctl add-flow ap_d0 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
        ap_d0.cmd('ovs-ofctl add-flow ap_d0 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
        ap_d0.cmd('ovs-ofctl add-flow ap_d0 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')

    info("*** Starting NFD processes\n")
    nfd1 = d0.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")
    nfd2 = h0.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")
    nfd3 = v0.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")
    nfd4 = s0.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")

    info("*** Creating faces and routes in d0\n")
    d0.cmd("nfdc face create udp://10.0.0.2")
    info(d0.cmd("nfdc route add /h0 udp://10.0.0.2"))
    info(d0.cmd("nfdc route add /v0 udp://10.0.0.2"))
    info(d0.cmd("nfdc route add /s0 udp://10.0.0.2"))

    info("*** Creating faces and routes in h0\n")
    h0.cmd("nfdc face create udp://10.0.0.3")
    h0.cmd("nfdc face create udp://10.0.0.1")
    h0.cmd("nfdc route add /v0 udp://10.0.0.3")
    h0.cmd("nfdc route add /s0 udp://10.0.0.3")

    info("*** Creating faces and routes in v0\n")
    v0.cmd("nfdc face create udp://10.0.0.4")
    v0.cmd("nfdc face create udp://10.0.0.2")
    v0.cmd("nfdc route add /s0 udp://10.0.0.4")

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping NFD\n")
    nfd1.kill()
    nfd2.kill()
    nfd3.kill()
    nfd4.kill()

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()