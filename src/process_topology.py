#!/usr/bin/python
"""
   Wrapper around Mininet WIFI to create NDN topologies.

   01/05/2021 - Andre Dexheimer Carneiro - andre.dxc@hotmail.com
"""

import sys
from functools import partial
# from mininet.log import setLogLevel, info, debug
from mininet.node import RemoteController
from mn_wifi.node import Station
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import configparser
import logging
import time

class Topology(object):

   def __init__(self):
      self.lstStations = []
      self.lstAccessPoints = []
      self.lstLinks = []
      # Mininet related
      self.lstNfdProcs = list()
      self.net = None

   def addStation(self, strName, **kwargs):
      self.lstStations.append(Node(strName, **kwargs))

   def addAccessPoint(self, strName, **kwargs):
      self.lstAccessPoints.append(Node(strName, **kwargs))

   def addLink(self, strNode1, strNode2, **kwargs):
      self.lstLinks.append(Link(strNode1, strNode2, **kwargs))

   def toString(self):
      logging.info('Stations (%d) ----------------' % len(self.lstStations))
      for pStation in self.lstStations:
         logging.info(pStation.toString() + '')

      logging.info('AccessPoints (%d) ----------------' % len(self.lstAccessPoints))
      for pAp in self.lstAccessPoints:
         logging.info(pAp.toString() + '')
         
      logging.info('Links (%d) ----------------' % len(self.lstLinks))
      for pLink in self.lstLinks:
         logging.info(pLink.toString() + '')

   def create(self):

      privateDirs = [('/var/log', '/tmp/%(name)s/var/log'), ('/var/run', '/tmp/%(name)s/var/run'), ('/run', '/tmp/%(name)s/run'), '/var/mn']
      station = partial( Station, privateDirs=privateDirs )
      self.net = Mininet_wifi(station=station)

      # Add access points
      for topoAp in self.lstAccessPoints:
         topoAp.kwargs['client_isolation'] = True
         self.net.addAccessPoint(topoAp.strName, protocols='OpenFlow13', ssid="simpletopo" + str(topoAp.strName), mode="g", channel="5", **topoAp.kwargs)
      
      # Add stations
      for topoStation in self.lstStations:
         self.net.addStation(topoStation.strName, **topoStation.kwargs)

      # Add controller
      c0 = self.net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

      logging.info("[Topology.create] Configuring wifi nodes")
      self.net.configureWifiNodes()

      logging.info("[Topology.create] Associating Stations")
      for topoLink in self.lstLinks:
         pNode1 = Topology.findNodeByName(topoLink.strNode1, self.net.aps + self.net.stations)
         pNode2 = Topology.findNodeByName(topoLink.strNode2, self.net.aps + self.net.stations)
         if (pNode1 is None) or (pNode2 is None):
            raise Exception('Could not find name in node list name1=%s name2=%s' % (topoLink.strNode1, topoLink.strNode2))
         else:
            self.net.addLink(pNode1, pNode2, **topoLink.kwargs)

      logging.info("[Topology.create] Starting network")
      self.net.build()
      c0.start()
      for pAp in self.net.aps:
         pAp.start([c0])

      for pAp in self.net.aps:
         if '-v' not in sys.argv:
            logging.info('Setting for ap=%s' % pAp.name)
            pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,arp,in_port=1,'
                     'actions=output:in_port,normal"')
            pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,icmp,in_port=1,'
                     'actions=output:in_port,normal"')
            pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,udp,in_port=1,'
                     'actions=output:in_port,normal"')
            pAp.cmd('ovs-ofctl add-flow ' + pAp.name + ' "priority=0,tcp,in_port=1,'
                     'actions=output:in_port,normal"')

      logging.info("[Topology.create] Starting NFD processes")
      for pStation in self.net.stations:
         nfdProc = pStation.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")
         self.lstNfdProcs.append(nfdProc)

      '''
      info("*** Creating faces and routes in sta1\n")
      sta1.cmd("nfdc face create udp://10.0.0.2")
      sta1.cmd("nfdc route add /sta2 udp://10.0.0.2")
      sta1.cmd("nfdc route add /sta3 udp://10.0.0.2")

      info("*** Creating faces and routes in sta2\n")
      sta2.cmd("nfdc face create udp://10.0.0.3")
      sta2.cmd("nfdc face create udp://10.0.0.1")
      sta2.cmd("nfdc route add /sta3 udp://10.0.0.3")
      '''
      '''
      ap_v0 = Topology.findNodeByName('ap_v0', self.net.aps)
      ap_d0 = Topology.findNodeByName('ap_d0', self.net.aps)
      ap_h0 = Topology.findNodeByName('ap_h0', self.net.aps)
      ap_s0 = Topology.findNodeByName('ap_s0', self.net.aps)
      v0 = Topology.findNodeByName('v0', self.net.stations)
      d0 = Topology.findNodeByName('d0', self.net.stations)
      h0 = Topology.findNodeByName('h0', self.net.stations)
      s0 = Topology.findNodeByName('s0', self.net.stations)

      v0.cmd("nfdc face create udp://%s" % d0.IP())
      v0.cmd("nfdc route add /v0 udp://%s" % d0.IP())
      v0.cmd("nfdc route add /d0 udp://%s" % d0.IP())
      v0.cmd("nfdc route add /h0 udp://%s" % d0.IP())
      v0.cmd("nfdc route add /s0 udp://%s" % d0.IP())

      d0.cmd("nfdc face create udp://%s" % v0.IP())
      d0.cmd("nfdc face create udp://%s" % h0.IP())
      d0.cmd("nfdc route add /h0 udp://%s" % h0.IP())
      d0.cmd("nfdc route add /s0 udp://%s" % h0.IP())

      h0.cmd("nfdc face create udp://%s" % d0.IP())
      h0.cmd("nfdc face create udp://%s" % s0.IP())
      h0.cmd("nfdc route add /s0 udp://%s" % s0.IP())

      s0.cmd("nfdc face create udp://%s" % h0.IP())
      '''
      # time.sleep(10)
      
      logging.info('[Topology.create] Creating and registering faces')
      for pStation in self.net.stations:
         for pStation2 in self.net.stations:
            if (pStation != pStation2):
               print('IP=%s' % pStation2.IP())
               pStation.cmd('nfdc face create udp://' + pStation2.IP())
               pStation.cmd('nfdc route add %s udp://%s' % (interestFilterForHost(pStation2.name), pStation2.IP()))

   def destroy(self):
      logging.info('')
      for proc in self.lstNfdProcs:
         proc.kill()

      logging.info("*** Stopping network")
      self.net.stop()

   def showCLI(self):
      logging.info("[Topology.showCLI] Running CLI")
      CLI(self.net)

   @staticmethod
   def fromFile(strFilePath):

      config = configparser.ConfigParser(delimiters=' ')
      config.read(strFilePath)
      topo = Topology()

      items = config.items('stations')
      logging.debug("Stations")
      for item in items:
         logging.debug(item[0].split(':'))
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
         logging.debug("APs")
         items = config.items('accessPoints')
         for item in items:
            logging.debug(item[0].split(':'))
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
         logging.debug("APs are optional")
         pass

      items = config.items('links')
      logging.debug("Links")
      for item in items:
         link = item[0].split(':')
         logging.debug(link)
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

   @staticmethod
   def findNodeByName(strName, lstNodes):
      for pNode in lstNodes:
         if (str(pNode) == strName):
            return pNode
      return None

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

def interestFilterForHost(strHost):
   return '/%s' % strHost
