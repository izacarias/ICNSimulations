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
from minindn.apps.nlsr import Nlsr
from minindn.apps.app_manager import AppManager
import configparser
import logging
import time
import subprocess
import random

class Topology(object):

   def __init__(self):
      self.lstStations = []
      self.lstAccessPoints = []
      self.lstLinks = []
      # Mininet related
      self.lstNfdProcs = list()
      self.lstLogFiles = list()
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

      # In preparation, kill any nfd processes that might be running
      subprocess.Popen('killall -9 nfd', shell=True)

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

      logging.info("[Topology.create] Starting NFD processes")
      self.lstLogFiles = list()
      self.lstNfdProcs = list()
      nCacheSize = 60000
      strNFDLogLevel = 'DEBUG'
      for pStation in self.net.stations:
         strHomeDir = '/tmp/%s/' % pStation.name
         strConfFile = strHomeDir + 'nfd.conf'
         strLogFile = strHomeDir + 'nfd.log'
         pStation.cmd('cp /usr/local/etc/ndn/nfd.conf.sample %s' % strConfFile)
         time.sleep(1)
         pStation.cmd('infoedit -f {} -s log.default_level -v {}'.format(strConfFile, strNFDLogLevel))
         pStation.cmd('infoedit -f {} -s tables.cs_max_packets -v {}'.format(strConfFile, nCacheSize))
         logfile = open(strLogFile, 'w')
         proc = pStation.popen("nfd --config %s" % (strConfFile), shell=True, stdout=logfile, stderr=logfile)
         self.lstLogFiles.append(logfile)
         self.lstNfdProcs.append(proc)

      # time.sleep(5)

      # for pStation in self.net.stations:
      #    nfdProc = pStation.popen("nfd --config /usr/local/etc/ndn/nfd.conf.sample")
      #    self.lstNfdProcs.append(nfdProc)

      logging.info('[Topology.create] Creating and registering faces')
      for pStation in self.net.stations:
         for pStation2 in self.net.stations:
            # sRand = random.randrange(9)
            if (pStation != pStation2):
               pStation.cmd('nfdc face create udp://' + pStation2.IP())
               pStation.cmd('nfdc route add %s udp://%s' % (interestFilterForHost(pStation2.name), pStation2.IP()))

      for pStation in self.net.stations:
         if ('params' not in pStation.params):
            pStation.params['params'] = {}

         if ('homeDir' not in pStation.params['params']):
            pStation.params['params']['homeDir'] = '/tmp/' + pStation.name

      nlsrs = AppManager(self.net.stations, Nlsr, logLevel='DEBUG')

   def destroy(self):
      logging.info('')
      for proc in self.lstNfdProcs:
         proc.kill()

      for pFile in self.lstLogFiles:
         pFile.close()

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
