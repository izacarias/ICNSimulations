import os
from mininet.log import setLogLevel, info
from mininet.node import RemoteController
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNWifiCLI, getPopen
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient
from time import sleep
# from icnexperiment.result_analysis import *

# This experiment uses the singleap topology and is intended to be a basic
# test case where we see if two nodes can send interests to each other.
# from icnexperiment.data_generation import curDatetimeToFloat

c_bShowCli = True

def runExperiment():
    setLogLevel('info')

    info("Starting network")
    ndnwifi = MinindnWifi(controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633), topoFile='/home/vagrant/icnsimulations/topologies/wifi-topo.conf')

    a = ndnwifi.net["h0"]
    b = ndnwifi.net["d0"]

    # Test for model-based mobility
    # if ndnwifi.args.modelMob:
    #     ndnwifi.startMobilityModel(model='GaussMarkov')
    #Test for replay based mobility
    # if ndnwifi.args.mobility:
    #     info("Running with mobility...")

    #     p1, p2, p3, p4 = dict(), dict(), dict(), dict()
    #     p1 = {'position': '40.0,30.0,0.0'}
    #     p2 = {'position': '40.0,40.0,0.0'}
    #     p3 = {'position': '31.0,10.0,0.0'}
    #     p4 = {'position': '200.0,200.0,0.0'}

    #     ndnwifi.net.mobility(a, 'start', time=1, **p1)
    #     ndnwifi.net.mobility(b, 'start', time=2, **p2)
    #     ndnwifi.net.mobility(a, 'stop', time=12, **p3)
    #     ndnwifi.net.mobility(b, 'stop', time=22, **p4)
    #     ndnwifi.net.stopMobility(time=23)
    #     ndnwifi.startMobility(time=0, mob_rep=1, reverse=False)

    ndnwifi.start()
    
    info("Setting unambiguous DPIDs\n")
    # os.system('ovs-vsctl set bridge ap_h0 other-config:datapath-id=1000000000000001')
    # os.system('ovs-vsctl set bridge ap_h1 other-config:datapath-id=1000000000000002')
    # os.system('ovs-vsctl set bridge ap_h2 other-config:datapath-id=1000000000000005')
    # os.system('ovs-vsctl set bridge ap_h3 other-config:datapath-id=1000000000000006')
    # os.system('ovs-vsctl set bridge ap_d0 other-config:datapath-id=1000000000000003')
    # os.system('ovs-vsctl set bridge ap_d1 other-config:datapath-id=1000000000000004')
    # os.system('ovs-vsctl set bridge ap_d2 other-config:datapath-id=1000000000000008')
    # os.system('ovs-vsctl set bridge ap_v0 other-config:datapath-id=1000000000000009')
    # os.system('ovs-vsctl set bridge ap_v1 other-config:datapath-id=1000000000000010')
    
    for pAp in ndn.net.aps:
        subprocess.call(['ovs-vsctl', 'set-controller', str(pAp), 'tcp:127.0.0.1:6633'])

    for pAp in ndn.net.aps:
        strApId = '1000000000' + str(nApId).zfill(6)
        subprocess.call(lstCmd)

    
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

        hshProducers[str(pHostOrig)] = getPopen(pHostOrig, 'producer %s' % interestFilterForHost(pHostOrig))

    # ndnwifi.net.plotGraph(max_x=100, max_y=100)
  
    # info("Instantiating consumers...\n")
    # nConsumers = 0
    # for pConsumer in ndnwifi.net.stations:
    #     for pProducer in ndnwifi.net.stations:
    #         if (pProducer != pConsumer):
    #             nConsumers += 1
    #             # Parametros do consumer: consumer <interesse> <nome_consumidor> <horario_float>
    #             getPopen(pConsumer, 'consumer %s/test %s %f' % (interestFilterForHost(pProducer), str(pConsumer), curDatetimeToFloat()))

            
    # Start the CLI
    if (c_bShowCli):
        MiniNDNWifiCLI(ndnwifi.net)
    ndnwifi.net.stop()
    ndnwifi.cleanUp()

def interestFilterForHost(pHost):
    return '/%s' % (str(pHost))

def curDatetimeToFloat():
    """
    Returns datetime as a float value
    """
    dtEpoch = datetime.utcfromtimestamp(0)
    dtNow   = datetime.now()
    return (dtNow - dtEpoch).total_seconds()

if __name__ == '__main__':
    try:
        runExperiment()
    except Exception as e:
        MinindnWifi.handleException()