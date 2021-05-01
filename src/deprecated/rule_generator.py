#!/usr/bin/python3
"""
draw_topology.py

Draws a topology read in the MiniNDN format.

22/12/2020        Andre Dexheimer Carneiro
"""
import sys
import logging

from icnexperiment.topology_generation import Topology, Link, Node, Station, AccessPoint
from icnexperiment.dir_config import c_strLogDir

c_strLogFile = c_strLogDir + 'rule_generator.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

class Rules():
   
   def __init__(self, strAPName):
      self.strAPName           = strAPName
      self.lstDestinationRules = []
      self.lstPriorityRules    = []

   def addDestinationRule(self, strDestination):
      self.lstDestinationRules.append(strDestination)
   
   def addPriorityRule(self, strDestHostName, nPriority):
      self.lstPriorityRules.append((strDestHostName, nPriority))
      self.lstPriorityRules.sort(key=lambda x: x[1])

   def toString(self):
      strReturn  = 'AP %s\n' % self.strAPName
      for node in self.lstDestinationRules:
         strReturn += node + '\n'
      for node in self.lstPriorityRules:
         strReturn += '%d - %s\n' % (node[1], node[0])
      return strReturn

def main():

   # Read input param
   if (len(sys.argv) == 1):
      logging.error('[main] No topology specified as first parameter!')
      exit()
   else:
      strTopoPath = sys.argv[1]

   pTopology = Topology.loadFromFile(strTopoPath)

   # Analyze each accesspoint individually
   for pAP in pTopology.lstAccessPoints:

      # Find all links connecting to this AP
      lstApLinks      = []
      lstStationLinks = []
      for pLink in pTopology.lstLinks:
         if (pLink not in lstApLinks) and ((pLink.origHost == pAP) or (pLink.destHost == pAP)):
            # Link connects to current AP
            if (type(linkDest(pLink, pAP)) == Station):
               lstStationLinks.append(pLink)
            elif (type(linkDest(pLink, pAP)) == AccessPoint):
               lstApLinks.append(pLink)
            else:
               Exception('[main] Link %s is connected to something other than AccessPoint or Station' % str(pLink))

      # Index 0 -> Best quality, Index n -> worst quality
      lstApLinks = orderLinksByQuality(lstApLinks)

      # Determine forwarding rules for AP
      apRules = Rules(pAP.strName)
      # Station link, send packat if destination matches endpoint IP
      for pLink in lstStationLinks:
         apRules.addDestinationRule(linkDest(pLink, pAP).strName)
      # AP link, send packet by sender/receiver priority
      for (nIndex, pLink) in enumerate(lstApLinks):
         apRules.addPriorityRule(linkDest(pLink, pAP).strName, nIndex)

      logging.info('[main] New Rule:')
      logging.info(apRules.toString())

def linkDest(pLink, pLinkOrig):
   """
   Returns the other host that this link is connected to.
   """
   if (pLink.origHost == pLinkOrig):
      return pLink.destHost
   elif (pLink.destHost == pLinkOrig):
      return pLink.origHost
   else:
      raise Exception('Link %s was not connected to %s' % (str(pLink), str(pLinkOrig)))

def orderLinksByQuality(lstLinks):
   """
   Orders links by quality (bandwidth) in a list.
   0 -> best, n -> worst
   """
   lstOut = []
   while (len(lstOut) < len(lstLinks)):
      pBestLink = None
      for pLink in lstLinks:
         if (pLink not in lstOut):
            if (pBestLink is None) or (pLink.nBandwidth >= pBestLink.nBandwidth):
               pBestLink = pLink
      
      lstOut.append(pBestLink)
   return lstOut

if (__name__ == '__main__'):
   main()
