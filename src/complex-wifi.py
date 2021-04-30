#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys

from functools import partial

from mininet.log import setLogLevel, info, debug
from mininet.node import RemoteController
from mn_wifi.node import Station
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import configparser

class Link(object):

   def __init__(self, strNode1, strNode2, **kwargs):
      self.strNode1 = strNode1
      self.strNode2 = strNode2
      self.kwargs = kwargs

class Node(object):

   def __init__(self, strName, **kwargs):
      self.strName = strName
      self.kwargs = kwargs

class MyTopology(object):

   def __init__(self):
      self.lstStations = []
      self.lstAccessPoints = []
      self.lstLinks = []

   def addStation(self, strName, **kwargs):
      info('New station name=%s\n' % strName)
      self.lstStations.append(Node(strName, **kwargs))

   def addAccessPoint(self, strName, **kwargs):
      self.lstAccessPoints.append(Node(strName, **kwargs))

   def addLink(self, strNode1, strNode2, **kwargs):
      self.lstLinks.append(Link(strNode1, strNode2, **kwargs))

   def toString(self):
      info('Stations (%d) ----------------\n' % len(self.lstStations))
      for pStation in self.lstStations:
         info('%s: %s\n' % (pStation.strName, str(['%s: %s;' % (str(x), str(y)) for x, y in pStation.kwargs.items()])))
      info('AccessPoints (%d) ----------------\n' % len(self.lstAccessPoints))
      info('Links (%d) ----------------\n' % len(self.lstLinks))

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

   topo = processTopo(topoFile='/home/vagrant/icnsimulations/topologies/test-topo.conf')

   hshAps = {}
   for pAp in topo.lstAccessPoints:
      hshAps[pAp.strName] = net.addAccessPoint(pAp.strName, protocols='OpenFlow13', ssid='simpletopo', mode='g', channel='5', kwargs=pAp.kwargs)
      
   hshStations = {}
   for pStation in topo.lstStations:
      hshStations[pStation.strName] = net.addStation(pStation.strName, kwargs=pStation.kwargs)

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
   nfd1 = sta1.popen("nfd")
   nfd2 = sta2.popen("nfd")
   nfd3 = sta3.popen("nfd")

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
   nfd1.kill()
   nfd2.kill()
   nfd3.kill()

   info("*** Stopping network\n")
   net.stop()

def processTopo(topoFile):
   config = configparser.ConfigParser(delimiters=' ')
   config.read(topoFile)
   topo = MyTopology()

   items = config.items('stations')
   debug("Stations")
   for item in items:
      debug(item[0].split(':'))
      name = item[0].split(':')[0]
      params = {}
      for param in item[1].split(' '):
         if (param == "_"):
            continue
         key = param.split('=')[0]
         value = param.split('=')[1]
         if key in ['range']:
            value = int(value)
         params[key] = value
      topo.addStation(name, **params)

   try:
      debug("APs")
      items = config.items('accessPoints')
      for item in items:
         debug(item[0].split(':'))
         name = item[0].split(':')[0]
         ap_params = {}
         for param in item[1].split(' '):
            if (param == "_"):
               continue
            key = param.split('=')[0]
            value = param.split('=')[1]
            if key in ['range']:
               value = int(value)
            ap_params[key] = value
      topo.addAccessPoint(name, **ap_params)
   except configparser.NoSectionError:
      debug("APs are optional")
      pass

   items = config.items('links')
   debug("Links")
   for item in items:
      link = item[0].split(':')
      debug(link)
      params = {}
      for param in item[1].split(' '):
            if param == "_":
               continue
            key = param.split('=')[0]
            value = param.split('=')[1]
            if key in ['bw', 'jitter', 'max_queue_size']:
               value = int(value)
            if key == 'loss':
               value = float(value)
            params[key] = value

      topo.addLink(link[0], link[1], **params)

   return topo

if __name__ == '__main__':
   setLogLevel('info')
   # topo = processTopo(topoFile='/home/vagrant/icnsimulations/topologies/test-topo.conf')
   # topo.toString()
   topology()
