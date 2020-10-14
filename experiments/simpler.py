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

from mininet.log import setLogLevel, info

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.helpers.ndnpingclient import NDNPingClient
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
import time

if __name__ == '__main__':
    setLogLevel('info')

    Minindn.cleanUp()
    Minindn.verifyDependencies()

    ndn = Minindn()

    ndn.start()

    info('Starting NFD on nodes\n')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    info('Starting NLSR on nodes\n')
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

    # Wait a little bit for NLSR
    time.sleep(20)

    # Run producer
    producer = ndn.net.hosts[0]
    strInterestFilter = '/myApp/' + producer.name
    strCmdAdvertise = 'nlsrc advertise ' + strInterestFilter
    strCmdProducer  = 'producer ' + strInterestFilter + ' &'
    print('CmdProducer: ' + strCmdAdvertise)
    print('CmdProducer: ' + strCmdProducer)
    producer.cmd(strCmdAdvertise)
    producer.cmd(strCmdProducer)
    time.sleep(1)

    # Run consumers
    nPings = 5
    for host in ndn.net.hosts:
        strCmdConsumer = 'consumer ' + strInterestFilter + ' ' + host.name
        print('CmdConsumer: ' + strCmdConsumer)
        host.cmd(strCmdConsumer)

        if (host != producer):
            res = NDNPingClient.ping(host, producer, nPings)
            print('Result for ' + host.name + ' ' + str(res))
    
    MiniNDNCLI(ndn.net)

    ndn.stop()
