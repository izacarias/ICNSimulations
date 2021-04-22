import os
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNWifiCLI, getPopen
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient
from minindn.apps.nlsr import Nlsr
import subprocess
from time import sleep
# from icnexperiment.result_analysis import *


c_bShowCli = True

def runExperiment():
    setLogLevel('info')

    info("Starting network")
    ndnwifi = MinindnWifi(controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633), topoFile='/home/vagrant/icnsimulations/topologies/topo-tiny.conf')
    
    ndnwifi.start()
    sleep(2)
        
    nApId = 1
    for pAp in ndnwifi.net.aps:
        strApId = '1000000000' + str(nApId).zfill(6)
        subprocess.call(['ovs-vsctl', 'set-controller', str(pAp), 'tcp:127.0.0.1:6633'])
        subprocess.call(['ovs-vsctl', 'set', 'bridge', str(pAp), 'other-config:datapath-id='+strApId])
        nApId += 1
    
    # Set IPs for access points
    nNextIP = 4
    lstIntfSet = []
    for pAp in ndnwifi.net.aps:
        lstIntf = pAp.intfList()
        for pIntf in lstIntf:
            strIntf = pIntf.name
            if (strIntf != 'lo') and (strIntf not in lstIntfSet):
                strIP = '10.0.0.' + str(nNextIP) + '/24'
                info('AP=%s; Intf=%s; IP=%s\n' % (str(pAp), strIntf, strIP))
                pAp.setIP(strIP, intf=pIntf)
                nNextIP += 1
                lstIntfSet.append(strIntf)

    # Set IPs for hosts
    for pStation in ndnwifi.net.stations:
        lstIntf = pStation.intfList()
        for pIntf in lstIntf:
            strIntf = pIntf.name
            if (strIntf != 'lo') and (strIntf not in lstIntfSet):
                strIP = '10.0.0.' + str(nNextIP) + '/24'
                info('STATION=%s; Intf=%s; IP=%s\n' % (str(pStation), strIntf, strIP))
                pStation.setIP(strIP, intf=pIntf)
                nNextIP += 1
                lstIntfSet.append(strIntf)
    

    info("Starting NFD\n")
    nfds  = AppManager(ndnwifi, ndnwifi.net.stations + ndnwifi.net.aps, Nfd)
    # nlsrs = AppManager(ndnwifi, ndnwifi.net.aps, Nlsr)

    # Create faces linking every node and instantiate producers
    info("Creating faces and instantiating producers...\n")
    hshProducers = {}
    for pHostOrig in ndnwifi.net.stations + ndnwifi.net.aps:
        for pHostDest in ndnwifi.net.stations + ndnwifi.net.aps:
            if (pHostDest != pHostOrig):
                info('Register, pHostOrig=%s; pHostDest=%s\n' % (str(pHostOrig), str(pHostDest)))
                Nfdc.createFace(pHostOrig, pHostDest.IP())
                Nfdc.registerRoute(pHostOrig, interestFilterForHost(pHostDest), pHostDest.IP())

        getPopen(pHostOrig, 'producer %s &' % interestFilterForHost(pHostOrig))

    # cons = ndnwifi.net.stations['h0']
    # getPopen(cons, 'consumer-with-timer h0')
            
    # Start the CLI
    if (c_bShowCli):
        MiniNDNWifiCLI(ndnwifi.net)
        
    ndnwifi.net.stop()
    ndnwifi.cleanUp()

def interestFilterForHost(pHost):
    return '/%s' % (str(pHost))

if __name__ == '__main__':
    try:
        runExperiment()
    except Exception as e:
        MinindnWifi.handleException()