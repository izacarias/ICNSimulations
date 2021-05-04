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

   def toString(self):
      strReturn = '<Link> %s <-> %s : %s' % (self.strNode1, self.strNode2, ['%s: %s' % (str(x), str(y)) for x, y in self.kwargs.items()])
      return strReturn

class Node(object):

   def __init__(self, strName, **kwargs):
      self.strName = strName
      self.kwargs = kwargs

   def toString(self):
      strReturn = '<Node> %s : %s' % (self.strName, ['%s: %s' % (str(x), str(y)) for x, y in self.kwargs.items()])
      return strReturn

class MyTopology(object):

   def __init__(self):
      self.lstStations = []
      self.lstAccessPoints = []
      self.lstLinks = []

   def addStation(self, strName, **kwargs):
      self.lstStations.append(Node(strName, **kwargs))

   def addAccessPoint(self, strName, **kwargs):
      self.lstAccessPoints.append(Node(strName, **kwargs))

   def addLink(self, strNode1, strNode2, **kwargs):
      self.lstLinks.append(Link(strNode1, strNode2, **kwargs))

   def toString(self):
      info('Stations (%d) ----------------\n' % len(self.lstStations))
      for pStation in self.lstStations:
         info(pStation.toString() + '\n')

      info('AccessPoints (%d) ----------------\n' % len(self.lstAccessPoints))
      for pAp in self.lstAccessPoints:
         info(pAp.toString() + '\n')
         
      info('Links (%d) ----------------\n' % len(self.lstLinks))
      for pLink in self.lstLinks:
         info(pLink.toString() + '\n')

def topology():

   privateDirs = [ ( '/var/log', '/tmp/%(name)s/var/log' ),
                  ( '/var/run', '/tmp/%(name)s/var/run' ),
                  ( '/run', '/tmp/%(name)s/run' ),
                     '/var/mn' ]
   station = partial( Station,
                  privateDirs=privateDirs )
   "Create a network."
   net = Mininet_wifi(station=station)
   
   topo = processTopo(topoFile='/home/vagrant/icnsimulations/topologies/wifi-topo12-noloop.conf')
   topo.toString()

   # Add access points
   for topoAp in topo.lstAccessPoints:
      topoAp.kwargs['client_isolation'] = True
      net.addAccessPoint(topoAp.strName, protocols='OpenFlow13', ssid="simpletopo" + str(topoAp.strName), mode="g", channel="5", **topoAp.kwargs)
   
   # Add stations
   for topoStation in topo.lstStations:
      net.addStation(topoStation.strName, **topoStation.kwargs)

   # Add controller
   c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

   info("*** Configuring wifi nodes\n")
   net.configureWifiNodes()

   info("*** Associating Stations\n")
   for topoLink in topo.lstLinks:
      pNode1 = findNodeByName(topoLink.strNode1, net.aps + net.stations)
      pNode2 = findNodeByName(topoLink.strNode2, net.aps + net.stations)
      if (pNode1 is None) or (pNode2 is None):
         raise Exception('Could not find name in node list name1=%s name2=%s' % (topoLink.strNode1, topoLink.strNode2))
      else:
         net.addLink(pNode1, pNode2, **topoLink.kwargs)

   info("*** Starting network\n")
   net.build()
   c0.start()
   for pAp in net.aps:
      pAp.start([c0])

   # if '-v' not in sys.argv:
   #    for pAp in net.aps:
   #       info('Setting for ap=%s' % pAp.name)
   #       pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,arp,in_port=1,'
   #                'actions=output:in_port,normal"')
   #       pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,icmp,in_port=1,'
   #                'actions=output:in_port,normal"')
   #       pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,udp,in_port=1,'
   #                'actions=output:in_port,normal"')
   #       pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,tcp,in_port=1,'
   #                'actions=output:in_port,normal"')

   info("*** Starting NFD processes\n")
   lstNfdProcs = list()
   for pStation in net.stations:
      nfdProc = pStation.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")
      lstNfdProcs.append(nfdProc)

   info('Creating and registering faces\n')
   for pStation in net.stations:
      for pStation2 in net.stations:
         if (pStation != pStation2):
            pStation.cmd("nfdc face create udp://" + pStation2.IP())
            pStation.cmd('nfdc route add %s udp://%s' % (interestFilterForHost(pStation2.name), pStation2.IP()))

   info("*** Running CLI\n")
   CLI(net)

   info("*** Stopping NFD\n")
   for proc in lstNfdProcs:
      proc.kill()

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

def interestFilterForHost(strHost):
   return '/%s' % strHost

def findNodeByName(strName, lstNodes):
   for pNode in lstNodes:
      if (str(pNode) == strName):
         return pNode
   return None

if __name__ == '__main__':
   setLogLevel('info')
   topology()
