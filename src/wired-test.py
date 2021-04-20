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
# from icnexperiment.result_analysis import *

c_bShowCli = True
c_strNFDLogLevel = 'NONE'
c_strNLSRLogLevel = 'NONE'

def runExperiment():
    setLogLevel('info')

    info("Starting network")
    ndn = Minindn(topoFile='/home/vagrant/icnsimulations/topologies/wired-topo8.conf')
    
    ndn.start()
        
    info("Starting NFD\n")
    sleep(2)

    nfds  = AppManager(ndn, ndn.net.hosts, Nfd, logLevel=c_strNFDLogLevel)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, logLevel=c_strNLSRLogLevel)

    # Create faces linking every node and instantiate producers
    info("Creating faces and instantiating producers...\n")
    hshProducers = {}
    for pHostOrig in ndn.net.hosts:
        info('Register, pHostOrig=%s\n' % (str(pHostOrig)))
        for pHostDest in ndn.net.hosts:
            if (pHostDest != pHostOrig):
                Nfdc.createFace(pHostOrig, pHostDest.IP())
                Nfdc.registerRoute(pHostOrig, interestFilterForHost(pHostDest), pHostDest.IP())

        getPopen(pHostOrig, 'producer %s &' % interestFilterForHost(pHostOrig))

    nPeriodMs = 700
    nMaxPackets = 100000
    for pHost in ndn.net.hosts:
        getPopen(pHost, 'consumer-with-timer %s %d %d' % (str(pHost), nPeriodMs, nMaxPackets))

    # sleep(nPeriodMs/1000.0*nMaxPackets)
    info('Sleeping...\n')
    # sleep(nPeriodMs/1000.0 * nMaxPackets)
    # sleep(20)

    # runLegacyConsumers(nPeriodMs, nMaxPackets, ndn.net.hosts)

    # cons = ndnwifi.net.stations['h0']
    # getPopen(cons, 'consumer-with-timer h0')
            
    # Start the CLI
    if (c_bShowCli):
        MiniNDNCLI(ndn.net)
        
    ndn.net.stop()
    ndn.cleanUp()

def runLegacyConsumers(nPeriodMs, nMaxPackets, lstHosts):

    dtBegin = datetime.now()
    dtLast = None
    nPackets = 0
    nPacketCount = 0
    while (nPackets < nMaxPackets):
        dtStart = datetime.now()
        if ((dtStart - dtLast).total_seconds()*1000.0 > nPeriodMs):
            # Send packets
            dtLast = datetime.now()
            for pHost in lstHosts:
                strProd = getRandomHostName(str(pHost), ndn.net.hosts)
                strInterest = interestFilterForHost(strProd) + '/' + str(nPackets)
                getPopen(pHost, 'consumer %s %d' % (strInterest, str(pHost)))    
                nPackets += 1

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