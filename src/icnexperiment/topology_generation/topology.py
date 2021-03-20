"""
Describes a topology with nodes (stations or access points) and links

Andre Dexheimer Carneiro 20/03/2021
"""

import logging
from .node import Node, Station, AccessPoint
from .link import Link

c_strNodesTag        = '[nodes]'
c_strLinksTag        = '[links]'
c_strStationsTag     = '[stations]'
c_strAccessPointsTag = '[accessPoints]'

class Topology:

    def __init__(self, lstNodes, lstLinks, lstAccessPoints=None):

        if (lstAccessPoints is None):
            lstAccessPoints = list()

        if (type(lstNodes) == type(lstLinks) == type(lstAccessPoints) == list):
            self.lstNodes = lstNodes
            self.lstLinks = lstLinks
            self.lstAccessPoints = lstAccessPoints
        else:
            raise Exception('Burro')

    def hasAccessPoints(self):
        return len(self.lstAccessPoints) > 0

    def areAllNodesConnected(self):
        """
        Checks the given topology for islands of nodes that are
        not connected to all other nodes.
        """
        bDone             = False
        lstLinksCopy      = self.lstLinks.copy()
        curLink           = lstLinksCopy[0]
        lstConnectedNodes = [curLink.origHost, curLink.destHost]
        i                 = 0
        lstLinksCopy.remove(curLink)
        while(not bDone):
            # Build lstConnectedNodes as we go
            # Find the first link connected to the connected nodes
            curLink = None
            for pLink in lstLinksCopy:
                if (pLink.origHost in lstConnectedNodes) or (pLink.destHost in lstConnectedNodes):
                    curLink = pLink

            if (curLink is not None):
                # Found a link, continue
                lstLinksCopy.remove(curLink)

                if (curLink.origHost not in lstConnectedNodes):
                    lstConnectedNodes.append(curLink.origHost)
                elif (curLink.destHost not in lstConnectedNodes):
                    lstConnectedNodes.append(curLink.destHost)

                # Increment index to rotate around the list
                i = i+1 if (i < len(lstLinksCopy)-1) else 0
            else:
                # There is no link left that connects to the nodes connected so far
                bDone = True

        # Create unconnected nodes list to see if they match
        lstUnconnectedNodes = []
        for pNode in self.lstNodes:
            if (pNode not in lstConnectedNodes):
                lstUnconnectedNodes.append(pNode)

        # There is no link left to visit
        if (len(lstConnectedNodes) == len(self.lstNodes)):
            # All nodes have already been connected
            logging.info('[Topology.areAllNodesConnected] All nodes are connected!')
            return True
        elif (len(lstLinksCopy) == 0):
            logging.error('[Topology.areAllNodesConnected] Visited all links but could not reach all nodes, lstConnectedNodes=%s' % str(lstConnectedNodes))
            logging.error('[Topology.areAllNodesConnected] Unconnected nodes=%s' % str(lstUnconnectedNodes))
            return False
        else:
            logging.error('[Topology.areAllNodesConnected] Could not reach all nodes, lstConnectedNodes=%s' % str(lstConnectedNodes))
            logging.error('[Topology.areAllNodesConnected] Unconnected nodes=%s' % str(lstUnconnectedNodes))
            return False

    def writeToFile(self, strPath):
        """
        Writes the output file for the topology in a MiniNDN or MiniNDNWifi readable format.
        """
        pFile = open(strPath, 'w')
        try:
            if (self.hasAccessPoints()):
                # MiniNDNWifi format
                # Stations
                pFile.write(c_strStationsTag + '\n')
                for pNode in self.lstNodes:
                    pFile.write(pNode.toTopoFile() + '\n')
                # AccessPoints
                pFile.write('\n' + c_strAccessPointsTag + '\n')
                for pNode in self.lstAccessPoints:
                    pFile.write(pNode.toTopoFile() + '\n')
            else:
                # MiniNDN format
                # Nodes
                pFile.write(c_strNodesTag + '\n')
                for pNode in self.lstNodes:
                    pFile.write(pNode.toTopoFile() + '\n')

            # Links
            pFile.write('\n' + c_strLinksTag + '\n')
            for pLink in self.lstLinks:
                pFile.write(pLink.toTopoFile() + '\n')
        except Exception as e:
            logging.error('Topology.writeToFile: Could not write to %s' % strPath)
            logging.error('writeToFile: Exception %s' % str(e))
        finally:
            pFile.close()

    @staticmethod
    def loadFromFile(strPath):
        """
        Loads topology from file into Topology a new object.
        """
        lstNodes    = []
        lstLinks    = []
        lstAPs      = []
        with open(strPath) as pFile:
            lstLines = pFile.readlines()
            bNodeSection = False
            bLinkSection = False
            for strLine in lstLines:
                # Begin the section where the hosts are described
                if (strLine.strip() == c_strNodesTag):
                    bNodeSection    = True
                    bLinkSection    = False
                    bStationSection = False
                    bAPSection      = False
                    continue
                # Begin links session, end of the hosts session
                if (strLine.strip() == c_strLinksTag):
                    bNodeSection    = False
                    bLinkSection    = True
                    bStationSection = False
                    bAPSection      = False
                    continue
                # Begin station sesion
                if (strLine.strip() == c_strStationsTag):
                    bNodeSection    = False
                    bLinkSection    = False
                    bStationSection = True
                    bAPSection      = False
                    continue
                # Begin access point sesion
                if (strLine.strip() == c_strAccessPointsTag):
                    bNodeSection    = False
                    bLinkSection    = False
                    bStationSection = False
                    bAPSection      = True
                    continue
                # Attempt to read hostnames in the following standard
                # b1: _ cache=0 radius=0.6 angle=3.64159265359
                if (bNodeSection) and (strLine.strip() != ''):
                    newNode = Node.fromString(strLine.strip())
                    lstNodes.append(newNode)
                    continue
                # Attempt to read station information in the following standard
                if (bStationSection) and (strLine.strip() != ''):
                    newNode = Station.fromString(strLine.strip())
                    lstNodes.append(newNode)
                    continue
                # Attempt to read access point information in the following standard
                if (bAPSection) and (strLine.strip() != ''):
                    newAP = AccessPoint.fromString(strLine.strip())
                    lstAPs.append(newAP)
                    continue
                # Attempt to read link information in the following standard
                # h0:h2 delay=10ms bw=1000 loss=12
                if (bLinkSection) and (strLine.strip() != ''):
                    newLink = Link.fromString(strLine.strip(), lstNodes + lstAPs)
                    lstLinks.append(newLink)
                    continue

        return Topology(lstNodes, lstLinks, lstAPs)