import os
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from minindn.minindn import Minindn
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNCLI, MiniNDNWifiCLI, getPopen
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient
import subprocess
from time import sleep
from datetime import datetime
# from icnexperiment.result_analysis import *

c_bShowCli = True
c_strNFDLogLevel  = 'DEBUG'
c_strNLSRLogLevel = 'DEBUG'

def runExperiment():
    setLogLevel('info')


    dtBegin = datetime.now()
    info("Starting network")
    ndn = Minindn(topoFile='/home/vagrant/icnsimulations/topologies/wired-topo4.conf')
    # ndn = Minindn(topoFile='/home/vagrant/icnsimulations/topologies/wired-switch.conf', controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633))

    ndn.start()

    # Properly connect switches to the SDN controller
    # nApId = 1
    # for pSwitch in ndn.net.switches:
    #     info('Setting up switch=%s\n3 vsctl', 'set-controller', str(pSwitch), 'tcp:127.0.0.1:6633'])
    #     subprocess.call(['ovs-vsctl', 'set', 'bridge', str(pSwitch), 'other-config:datapath-id='+strApId])
    #     nApId += 1

    # Properly set IPs for all interfaces
    # nNextIP = 10
    # lstIntfSet = []
    # for pNode in ndn.net.switches + ndn.net.hosts:
    #     lstIntf = pNode.intfList()
    #     for pIntf in lstIntf:
    #         strIntf = pIntf.name
    #         if (strIntf != 'lo') and (strIntf not in lstIntfSet):
    #             strIP = '10.0.0.' + str(nNextIP) + '/24'
    #             info('Node=%s; Interface=%s; IP=%s\n' % (str(pNode), strIntf, strIP))
    #             pNode.setIP(strIP, intf=pIntf)
    #             nNextIP += 1
    #             lstIntfSet.append(strIntf)

    '''
    Node=sw1; Interface=sw1-eth1; IP=10.0.0.10/24
    Node=sw1; Interface=sw1-eth2; IP=10.0.0.11/24
    Node=sw2; Interface=sw2-eth1; IP=10.0.0.12/24
    Node=sw2; Interface=sw2-eth2; IP=10.0.0.13/24
    Node=d0; Interface=d0-eth0; IP=10.0.0.14/24
    Node=d0; Interface=d0-eth1; IP=10.0.0.15/24
    Node=h0; Interface=h0-eth0; IP=10.0.0.16/24
    Node=v0; Interface=v0-eth0; IP=10.0.0.17/24
    '''

    info("Starting NFD and NLSR\n")
    sleep(2)

    nfds  = AppManager(ndn, ndn.net.hosts, Nfd, logLevel=c_strNFDLogLevel)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, logLevel=c_strNLSRLogLevel)

    # Create faces linking every node and instantiate producers
    info("Creating faces and instantiating producers...\n")
    hshProducers = {}
    nHostsSet = 1
    for pHostOrig in ndn.net.hosts:
        info('Register, pHostOrig=%s %d/%d\n' % (str(pHostOrig), nHostsSet, len(ndn.net.hosts)))
        for pHostDest in ndn.net.hosts:
            if (pHostDest != pHostOrig):
                Nfdc.createFace(pHostOrig, pHostDest.IP())
                Nfdc.registerRoute(pHostOrig, interestFilterForHost(pHostDest), pHostDest.IP())

        getPopen(pHostOrig, 'producer %s &' % interestFilterForHost(pHostOrig))
        nHostsSet += 1

    # nPeriodMs = 700
    # nMaxPackets = 1000
    # for pHost in ndn.net.hosts:
    #     getPopen(pHost, 'consumer-with-timer %s %d %d' % (str(pHost), nPeriodMs, nMaxPackets  
    
    for pHost in ndn.net.hosts:
        strCmd1 = 'export HOME=/tmp/minindn/%s; ' % str(pHost)
        strCmd2 = 'consumer-with-queue %s /home/vagrant/icnsimulations/topologies/queue_wired-topo4.txt &' % (str(pHost))
        strCmd  = strCmd1 + strCmd2
        info('cmd: %s\n' % strCmd)
        # pHost.cmd(strCmd)
        getPopen(pHost, 'consumer-with-queue %s /home/vagrant/icnsimulations/topologies/queue_wired-topo4.txt &' % (str(pHost)))
    
    dtDelta = datetime.now() - dtBegin
    info('Done setting up, took %.2f seconds\n' % dtDelta.total_seconds())
            
    # Start the CLI
    if (c_bShowCli):
        MiniNDNCLI(ndn.net)
        
    ndn.net.stop()
    ndn.cleanUp()

def getRandomHostName(strHost, lstHosts):
    nIndex = -1
    while (nIndex < 0) or (str(lstHosts[nIndex]) == strHost):
        nIndex = rand() % len(lstHosts)
    return str(lstHosts[nIndex])

def interestFilterForHost(pHost):
    return '/ndn/%s-site/%s' % (str(pHost), str(pHost))

if __name__ == '__main__':
    try:
        runExperiment()
    except Exception as e:
        MinindnWifi.handleException()