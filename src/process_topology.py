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
import networkx as nx
from random_talks import RandomTalks

# Each unit of cache is equivalent to aprox. 8KB
c_nMaxCacheSize = 80000
# c_nMaxCacheSize = 20000

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

   def create(self, strMode='icn', sCacheRatio=1.0):

      logging.info('[Topology.create] mode=%s, cacheRatio=%f' % (strMode, sCacheRatio))

      # Preparation
      # Kill any nfd processes that might be running
      subprocess.Popen('killall -9 nfd', shell=True)
      # Remove anything in the host directories - does not seem necessary
      # subprocess.Popen('rm -fr /tmp/icnsimulations')

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
      strNFDLogLevel = 'DEBUG'
      for pStation in self.net.stations:
         nCacheSize = self.cacheSizeForHost(pStation.name, strMode, sCacheRatio)
         logging.info('[Topology.create] host=%s cacheRatio=%.2f, cacheSize=%d' % (pStation.name, sCacheRatio, nCacheSize))
         strHomeDir = '/tmp/icnsimulations/%s/' % pStation.name
         pStation.cmd('mkdir -p %s' % strHomeDir)
         strConfFile = strHomeDir + 'nfd.conf'
         strLogFile = strHomeDir + 'nfd.log'
         pStation.cmd('cp /usr/local/etc/ndn/nfd.conf.sample %s' % strConfFile)
         pStation.cmd('infoedit -f {} -s log.default_level -v {}'.format(strConfFile, strNFDLogLevel))
         pStation.cmd('infoedit -f {} -s tables.cs_max_packets -v {}'.format(strConfFile, nCacheSize))
         logfile = open(strLogFile, 'w')
         proc = pStation.popen("nfd --config %s" % (strConfFile), shell=True, stdout=logfile, stderr=logfile)
         self.lstLogFiles.append(logfile)
         self.lstNfdProcs.append(proc)

      self.createNfdRoutes()

      if (strMode == 'icn_sdn') or (strMode == 'ip_sdn'):
         self.setSdnFilters(self.net.aps)

   def setSdnFilters(self, lstAps):
      hshAPs = self.getApToHostMap()
      for pAp in lstAps:
         for strIntf in pAp.intfNames():
            if (strIntf.find('wlan') >= 0):
               nMaxBandwidth = 50
               nBandLimit = int(self.getPriorityByHostName(hshAPs[pAp.name])*nMaxBandwidth)
               pHost = Topology.findNodeByName(hshAPs[pAp.name], self.net.stations)
               logging.info('[Topology.setSdnFilters] Host %s for ap %s via %s has nBandLimit=%d' % (pHost.name, strIntf, pAp.name, nBandLimit))
               subprocess.Popen('tc qdisc del dev %s root' % strIntf, shell=True)
               subprocess.Popen('tc qdisc add dev %s root handle 1: htb default 1 direct_qlen 1000' % strIntf, shell=True)
               subprocess.Popen('tc class add dev %s classid 1:fffe htb rate 54mbit ceil 54mbit burst 1500b cburst 1500b' % strIntf, shell=True)
               subprocess.Popen('tc class add dev %s classid 1:fa parent 1:fffe htb rate 12Kbit ceil %dMbit burst 512b cburst 512b' % (strIntf, nBandLimit), shell=True)
               subprocess.Popen('tc filter add dev %s parent 1: prio 1 protocol ip handle 0xfa fw flowid 1:fa action ok' % strIntf, shell=True)
               subprocess.Popen('ovs-ofctl -O OpenFlow13 add-flow %s \"table=0,priority=10,ip,nw_src=%s,actions=set_field:250->pkt_mark,goto_table:1\"' % (pAp.name, pHost.IP()), shell=True)
               '''
               tc qdisc del dev ap1-wlan1 root
               tc qdisc add dev ap1-wlan1 root handle 1: htb default 1 direct_qlen 1000
               tc class add dev ap1-wlan1 classid 1:fffe htb rate 54mbit ceil 54mbit burst 1500b cburst 1500b
               tc class add dev ap1-wlan1 classid 1:fa parent 1:fffe htb rate 12Kbit ceil 2Mbit burst 512b cburst 512b
               tc filter add dev ap1-wlan1 parent 1: prio 1 protocol ip handle 0xfa fw flowid 1:fa action ok
               ovs-ofctl -O OpenFlow13 add-flow ap1 "table=0,priority=10,ip,nw_src=10.0.0.3,nw_dst=10.0.0.1,actions=set_field:250->pkt_mark,goto_table:1"
               '''

   def getPriorityByHostName(self, strHost):
      strType = Node.getHostTypeByName(strHost)
      if (strType == 'vehicle'):
         return 1.0
      elif (strType == 'drone'):
         return 0.75
      elif (strType == 'human'):
         return 0.5
      elif (strType == 'sensor'):
         return 0.25
      else:
         raise Exception('Unrecognizes host type %s for host=%s' % (strType, strHost))

   def cacheSizeForHost(self, strHost, strMode, sCacheRatio=1.0):
      if (strMode == 'icn') or (strMode == 'icn_sdn'):
         if (strHost[0] == 'v'):
            return c_nMaxCacheSize*sCacheRatio
         elif (strHost[0] == 'h'):
            return int(0.75*c_nMaxCacheSize*sCacheRatio)
         elif (strHost[0] == 'd'):
            return int(0.75*c_nMaxCacheSize*sCacheRatio)
         elif (strHost[0] == 's'):
            return int(0.5*c_nMaxCacheSize*sCacheRatio)
      elif (strMode == 'ip') or (strMode == 'ip_sdn'):
         return 0
      else:
         raise Exception('[Topology.cacheSizeForHost] Unrecognized mode=%s' % strMode)

   def createNfdRoutes(self):

      logging.info('[Topology.createNfdRoutes] Creating routes for %d stations and %d APs' % (len(self.net.stations), len(self.net.aps)))
      lstHostLinks = self.abstractApsFromLinks()
      # Create faces to all neighbouring hosts
      for pStation in self.net.stations:
         for topoLink in lstHostLinks:
            strDest = topoLink.connectsTo(pStation.name)
            pDestHost = Topology.findNodeByName(strDest, self.net.stations)
            if (pDestHost):
               # logging.info('[Topology.createNfdRoutes] Host %s is connected to %s (%s)' % (pStation.name, pDestHost.name, pDestHost.IP()))
               pStation.cmd('nfdc face create udp://' + pDestHost.IP())

      # Create routes between faces
      # Create NX graph for the network topology
      pGraph = nx.Graph()
      for pLink in lstHostLinks:
         nWeight = 0
         if ('delay' in pLink.kwargs):
            strDelay = pLink.kwargs['delay']
            nPos = strDelay.find('ms')
            if (nPos > 0):
               # Remove ms suffix
               nWeight = int(strDelay[0:nPos])
            else:
               nWeight = int(strDelay)
         pGraph.add_edge(pLink.strNode1, pLink.strNode2, weight=nWeight)

      # Create routes starting on each host
      for pStart in self.net.stations:
         # logging.info('[Topology.createNfdRoutes] Paths for start=%s' % pStart.name)
         for pEnd in self.net.stations:
            if (pStart != pEnd):
               lstPath = nx.shortest_path(pGraph, pStart.name, pEnd.name, weight='weight')
               if (len(lstPath) >= 2):
                  strNextHost = lstPath[1]
                  pNextHost = Topology.findNodeByName(strNextHost, self.net.stations)
               else:
                  raise Exception('There should be at least 2 hosts in the route between %s and %s' % (pStart.name, pEnd.name))
               # logging.info('[Topology.createNfdRoutes] Host %s for filter=%s, nextHost=%s (%s)' % (pStart.name, RandomTalks.getFilterByHostname(pEnd.name), pNextHost.name, pNextHost.IP()))
               pStart.cmd('nfdc route add %s udp://%s' % (RandomTalks.getFilterByHostname(pEnd.name), pNextHost.IP()))

      # logging.info('[Topology.createNfdRoutes] Done')

   def abstractApsFromLinks(self):
      """
      Returns a list of links connecting all the stations by removing any intermediary access points.
      """
      # Find out which APs connect to which hosts
      hshAPs = {}
      lstNewLinks = list()
      for topoLink in self.lstLinks:
         strAp = strHost = ''
         if (Node.isAccessPoint(topoLink.strNode1) and (not Node.isAccessPoint(topoLink.strNode2))):
            strAp = topoLink.strNode1
            strHost = topoLink.strNode2
         elif (Node.isAccessPoint(topoLink.strNode2) and (not Node.isAccessPoint(topoLink.strNode1))):
            strAp = topoLink.strNode2
            strHost = topoLink.strNode1
         elif (Node.isAccessPoint(topoLink.strNode1) and Node.isAccessPoint(topoLink.strNode2)):
            # This connects two APs
            lstNewLinks.append(topoLink)
         else:
            raise Exception('Link %s connects two hosts. Why?' % str(topoLink))

         if (strAp != '') and (strHost != ''):
            hshAPs[strAp] = strHost

      # Replace any AP referenced in the links with its equivalent host
      for topoLink in lstNewLinks:
         if (Node.isAccessPoint(topoLink.strNode1)):
            topoLink.strNode1 = hshAPs[topoLink.strNode1]
         else:
            raise Exception('Something is wrong 1')

         if (Node.isAccessPoint(topoLink.strNode2)):
            topoLink.strNode2 = hshAPs[topoLink.strNode2]
         else:
            raise Exception('Something is wrong 2')

      return lstNewLinks

   def getApToHostMap(self):
      hshAPs = {}
      for topoLink in self.lstLinks:
         strAp = strHost = ''
         if (Node.isAccessPoint(topoLink.strNode1) and (not Node.isAccessPoint(topoLink.strNode2))):
            strAp = topoLink.strNode1
            strHost = topoLink.strNode2
         elif (Node.isAccessPoint(topoLink.strNode2) and (not Node.isAccessPoint(topoLink.strNode1))):
            strAp = topoLink.strNode2
            strHost = topoLink.strNode1
         if (strAp != '') and (strHost != ''):
            hshAPs[strAp] = strHost
      return hshAPs

   def clearAllCache(self):

      lstFilters = list()
      for pStation in self.net.stations:
         lstFilters.append(RandomTalks.getFilterByHostname(pStation.name))

      for pStation in self.net.stations:
         for strFilter in lstFilters:
            pStation.cmd('nfdc cs erase %s' % strFilter)

      logging.info('[RandomTalks.clearAllCache] Everything erased!')
      return

   def destroy(self):
      logging.info('')
      for proc in self.lstNfdProcs:
         proc.kill()

      for pFile in self.lstLogFiles:
         pFile.close()

      subprocess.Popen('killall -9 putchunks', shell=True)
      subprocess.Popen('killall -9 catchunks', shell=True)

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

   def connectsTo(self, strHost):
      if (self.strNode1 == strHost):
         return self.strNode2
      elif (self.strNode2 == strHost):
         return self.strNode1
      else:
         return ''

class Node(object):

   def __init__(self, strName, **kwargs):
      self.strName = strName
      self.kwargs = kwargs

   def toString(self):
      strReturn = '<Node> %s : %s' % (self.strName, ['%s: %s' % (str(x), str(y)) for x, y in self.kwargs.items()])
      return strReturn

   @staticmethod
   def getHostTypeByName(strName):
      if (strName[0] == 'v'):
         return 'vehicle'
      elif (strName[0] == 'h'):
         return 'human'
      elif (strName[0] == 'd'):
         return 'drone'
      elif (strName[0] == 's'):
         return 'sensor'
      else:
         raise Exception('Unrecognized host type with name=%s' % strName)

   @staticmethod
   def isAccessPoint(strName):
      if ('ap' in strName):
         return True
      else:
         return False

def interestFilterForHost(strHost):
   return '/%s' % strHost
