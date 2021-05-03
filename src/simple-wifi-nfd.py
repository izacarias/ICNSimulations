#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys

from functools import partial

from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from mn_wifi.node import Station
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import subprocess


def topology():
    
    privateDirs = [ ( '/var/log', '/tmp/%(name)s/var/log' ),
                    ( '/var/run', '/tmp/%(name)s/var/run' ),
                    ( '/run', '/tmp/%(name)s/run' ),
                      '/var/mn' ]
    station = partial( Station,
                    privateDirs=privateDirs )
    "Create a network."
    net = Mininet_wifi(station=station)
    hshNodeTypes = {'sta1': 'human', 'sta2': 'drone', 'sta3': 'vehicle'}

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


    ap1 = net.addAccessPoint('ap1', protocols='OpenFlow13', ssid="simpletopo", mode="g",
                             channel="5", **ap_arg)
    
    ap2 = net.addAccessPoint('ap2', protocols='OpenFlow13', ssid="simpletopo2", mode="g",
                             channel="11", **ap_arg)
    
    ap3 = net.addAccessPoint('ap3', protocols='OpenFlow13', ssid="simpletopo3", mode="g",
                             channel="11", **ap_arg)

    sta1 = net.addStation('sta1', **sta_arg)
    sta2 = net.addStation('sta2')
    sta3 = net.addStation('sta3')
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap2)
    net.addLink(sta3, ap3)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])
    ap3.start([c0])

    info("*** Setting priorities\n")
    setNodePriorities(net.aps, hshNodeTypes)

    if '-v' not in sys.argv:
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,arp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,icmp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,udp,in_port=1,'
                'actions=output:in_port,normal"')
        ap1.cmd('ovs-ofctl add-flow ap1 "priority=0,tcp,in_port=1,'
                'actions=output:in_port,normal"')

    info("*** Starting NFD processes\n")

    lstNfdProcs = list()
    lstLogFiles = list()
    nCacheSize = 6000
    strNFDLogLevel = 'DEBUG'
    for pStation in net.stations:
        strHomeDir = '/tmp/%s/' % pStation.name
        strConfFile = strHomeDir + 'nfd.conf'
        strLogFile = strHomeDir + 'nfd.log'
        pStation.cmd('cp /usr/local/etc/ndn/nfd.conf.sample %s' % strConfFile)
        pStation.cmd('infoedit -f {} -s log.default_level -v {}'.format(strConfFile, strNFDLogLevel))
        pStation.cmd('infoedit -f {} -s tables.cs_max_packets -v {}'.format(strConfFile, nCacheSize))
        logfile = open(strLogFile, 'w')
        proc = pStation.popen("nfd --config %s" % (strConfFile), shell=True, stdout=logfile, stderr=logfile)
        lstLogFiles.append(logfile)
        lstNfdProcs.append(proc)
            
    # nfd2 = sta2.popen("nfd --config /tmp/sta2/nfd.conf")
    # nfd3 = sta3.popen("nfd --config /tmp/sta3/nfd.conf")

    info("*** Creating faces and routes in sta1\n")
    sta1.cmd("nfdc face create udp://10.0.0.2")
    sta1.cmd("nfdc route add /sta2 udp://10.0.0.2")
    sta1.cmd("nfdc route add /sta3 udp://10.0.0.2")

    info("*** Creating faces and routes in sta2\n")
    sta2.cmd("nfdc face create udp://10.0.0.3")
    sta2.cmd("nfdc face create udp://10.0.0.1")
    sta2.cmd("nfdc route add /sta3 udp://10.0.0.3")

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping NFD\n")
    for proc in lstNfdProcs:
        proc.kill()

    for pFile in lstLogFiles:
        pFile.close()

    info("*** Stopping network\n")
    net.stop()

def setNodePriorities(lstAps, hshNodeTypes):
    strPrefix = 'sta'
    nMaxBandKb = 10000
    for pAp in lstAps:
        strStation = strPrefix + pAp.name[-1]
        strType = hshNodeTypes[strStation]
        strIface = pAp.name + '-wlan1'

        if (strType == 'human'):
            nBand = nMaxBandKb
        elif (strType == 'vehicle'):
            nBand = int(0.75 * nMaxBandKb)
        elif (strType == 'drone'):
            nBand = int(0.5 * nMaxBandKb)
        else:
            raise Exception('Unrecognized host type=%s' % strType)

        print('[setNodePriorities] interface=%s set to %d kbps' % (strIface, nBand))
        subprocess.Popen('ovs-vsctl set interface %s ingress_policing_rate=%d' % (strIface, nBand), shell=True)
        subprocess.Popen('ovs-vsctl set interface %s ingress_policing_burst=%d' % (strIface, nBand/10), shell=True)

def getStationByName(strName, lstStations):
    for pStation in lstStations:
        if (pStation.name == strName):
            return pStation
    return None

if __name__ == '__main__':
    setLogLevel('info')
    topology()
