# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2020, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

from mininet.log import setLogLevel, info, debug
from mininet.node import RemoteController, Ryu
from minindn.wifi.minindnwifi import MinindnWifi
from minindn.util import MiniNDNWifiCLI, getPopen
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.helpers.nfdc import Nfdc
from minindn.helpers.ndnpingclient import NDNPingClient
from time import sleep
from icnexperiment.result_analysis import *
from datetime import datetime
import subprocess

# This experiment uses the singleap topology and is intended to be a basic
# test case where we see if two nodes can send interests to each other.
# from icnexperiment.data_generation import curDatetimeToFloat

c_bShowCli = True

def runExperiment():
    setLogLevel('info')

    info("Starting network")
    ndnwifi = MinindnWifi(controller=RemoteController, topoFile='/home/vagrant/icnsimulations/topologies/wifi-topo-close.conf')

    # a = ndnwifi.net["h0"]
    # b = ndnwifi.net["d0"]

    # # Test for model-based mobility
    # if ndnwifi.args.modelMob:
    #     ndnwifi.startMobilityModel(model='GaussMarkov')
    # #Test for replay based mobility
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
    info("Starting NFD...\n")
    sleep(2)
    nfds = AppManager(ndnwifi, ndnwifi.net.stations, Nfd)

    # Create faces linking every node and instantiate producers
    info('Creating faces and instantiating producers...\n')
    hshProducers = {}
    for pHostOrig in ndnwifi.net.stations:
        for pHostDest in ndnwifi.net.stations:
            if (pHostDest != pHostOrig):
                debug('Register, pHostOrig=%s; pHostDest=%s\n' % (str(pHostOrig), str(pHostDest)))
                Nfdc.createFace(pHostOrig, pHostDest.IP())
                Nfdc.registerRoute(pHostOrig, interestFilterForHost(pHostDest), pHostDest.IP())

        hshProducers[str(pHostOrig)] = getPopen(pHostOrig, 'producer %s' % interestFilterForHost(pHostOrig))

    info('Connecting stations to remote controller...\n')
    for pAp in ndnwifi.net.aps:
        subprocess.call(['ovs-vsctl', 'set-controller', str(pAp), 'tcp:127.0.0.1:6633'])  
  
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

        # netstat
        # ovs-vsctl set-controller ap_h0 tcp:127.0.0.1:6633
        
        # python ./pox.py -- verbose samples.pretty_log forwarding.l2_learning