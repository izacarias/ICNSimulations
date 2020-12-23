"""
topology_generator.py

Custom topology generator. Returns MiniNDN readable .conf file for different topologies.

22/12/2020          Andre Dexheimer Carneiro
"""
import logging
import sys
from .link import Link
from .node import Node

# ---------------------------------------------------------------------- Constants
c_nDefaultNodeLinks = 5
c_strNodesTag       = '[nodes]'
c_strLinksTag       = '[links]'

class TopologyGenerator:
    """
    Creates MiniNDN readable topologies.
    """

    @staticmethod
    def createRandomTopo(lstHosts, nNodeLinks=c_nDefaultNodeLinks):
        """
        Places all hosts randomly in a X,Y space and stabilishes connections with the N hosts closest to each one.
        """
        c_nX = 100
        c_nY = 100
        logging.info('createRandomTopo: begin maxX=%d, maxY=%d, NodeLinks=%d' % (c_nX, c_nY, nNodeLinks))

        # Place all nodes at random x,y coordinates
        lstNodes = []
        lstLinks = []
        for strHost in lstHosts:
            newNode = Node(strHost)
            newNode.placeAtRandom(c_nX, c_nY)
            lstNodes.append(newNode)

        # Create links for each node
        for i in range(len(lstNodes)):
            lstDistances = []
            pNode        = lstNodes[i]

            # Calculate all distances
            for j in range(len(lstNodes)):
                # Elements are added to the list as a tuple (index, distance)
                if (j != i):
                    lstDistances.append((j, pNode.distanceTo(lstNodes[j])))
                    logging.debug('createRandomTopo: distance from %s to %s = %f' % (pNode.Name(), lstNodes[j].Name(), lstDistances[-1][1]))

            # Order the list by distance (tuple field 1)
            lstDistances.sort(key=lambda x: x[1])
            # Select the N closest nodes and create the links
            for tupleNode in lstDistances[0:min(len(lstDistances), nNodeLinks)]:
                # Create the links
                newLink = Link(pNode, lstNodes[tupleNode[0]])
                lstLinks.append(newLink)
                logging.debug('createRandomTopo: Node %s links to %s' % (newLink.origHost.Name(), newLink.destHost.Name()))

        return lstNodes, lstLinks

    @staticmethod
    def writeTopoFile(lstNodes, lstLinks, strPath):
        """
        Writes the output file for the topology in a MiniNDN readable format
        """
        with open(strPath, 'w') as pFile:
            pFile.write(c_strNodesTag + '\n')
            for pNode in lstNodes:
                pFile.write(pNode.toTopoFile() + '\n')
            pFile.write(c_strLinksTag + '\n')
            for pLink in lstLinks:
                pFile.write(pLink.toTopoFile() + '\n')

    @staticmethod
    def createHostList(nHumans, nDrones, nSensors, nVehicles):
        """
        Creates a hostname list based on the constants defining number of nodes of each kind
        """
        lstHosts = []
        for i in range(nHumans):
            lstHosts.append('h' + str(i))
        for i in range(nDrones):
            lstHosts.append('d' + str(i))
        for i in range(nSensors):
            lstHosts.append('s' + str(i))
        for i in range(nVehicles):
            lstHosts.append('v' + str(i))
        return lstHosts

    @staticmethod
    def readTopoFile(strPath):
        """
        Reads a MiniNDN formated topology .conf file. Returns nodes list and link list
        """
        lstNodes = []
        lstLinks = []
        with open(strPath) as pFile:
            lstLines = pFile.readlines()
            bNodeSection = False
            bLinkSection = False
            for strLine in lstLines:
                # Begin the section where the hosts are described
                if (strLine.strip() == c_strNodesTag):
                    bNodeSection = True
                    bLinkSection = False
                    continue
                # Begin links session, end of the hosts session
                if (strLine.strip() == c_strLinksTag):
                    bNodeSection = False
                    bLinkSection = True
                    continue
                # Attempt to read hostnames in the following standard
                # b1: _ cache=0 radius=0.6 angle=3.64159265359
                if (bNodeSection):
                    newNode = Node.fromString(strLine)
                    lstNodes.append(newNode)
                # Attempt to read link information in the following standard
                # h0:h2 delay=10ms bw=1000 loss=12
                if (bLinkSection):
                    newLink = Link.fromString(strLine, lstNodes)
                    lstLinks.append(newLink)
                    continue

        return (lstNodes, lstLinks)

    @staticmethod
    def checkForIslands(lstNodes, lstLinks):
        """
        Checks the given topology for islands of nodes that are not connected to all other nodes.
        """
        raise NotImplementedError('opa')