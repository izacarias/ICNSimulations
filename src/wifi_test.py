import os
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNWifiCLI, getPopen
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient
import subprocess
from time import sleep
# from icnexperiment.result_analysis import *


c_bShowCli = True

def runExperiment():
    setLogLevel('info')

    info("Starting network")
    ndnwifi = MinindnWifi(controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633), topoFile='/home/vagrant/icnsimulations/topologies/wifi-topo-close.conf')
    
    ndnwifi.start()
    
    nApId = 1
    for pAp in ndnwifi.net.aps:
        strApId = '1000000000' + str(nApId).zfill(6)
        subprocess.call(['ovs-vsctl', 'set-controller', str(pAp), 'tcp:127.0.0.1:6633'])
        subprocess.call(['ovs-vsctl', 'set', 'bridge', str(pAp), 'other-config:datapath-id='+strApId])
        nApId += 1
    
    info("Starting NFD\n")
    sleep(2)

    nfds = AppManager(ndnwifi, ndnwifi.net.stations, Nfd)

    # Create faces linking every node and instantiate producers
    info("Creating faces and instantiating producers...\n")
    hshProducers = {}
    for pHostOrig in ndnwifi.net.stations:
        for pHostDest in ndnwifi.net.stations:
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