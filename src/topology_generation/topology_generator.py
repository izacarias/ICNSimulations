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
c_nDefaultX         = 100
c_nDefaultY         = 100

class TopologyGenerator:
    """
    Creates MiniNDN readable topologies.
    """

    @staticmethod
    def createRandomTopo(lstHosts, nNodeLinks=c_nDefaultNodeLinks, nMaxX=c_nDefaultX, nMaxY=c_nDefaultY):
        """
        Places all hosts randomly in a X,Y space and stabilishes connections with the N hosts closest to each one.
        """
        logging.info('[createRandomTopo] Begin maxX=%d, maxY=%d, NodeLinks=%d' % (nMaxX, nMaxY, nNodeLinks))

        # Place all nodes at random x,y coordinates
        lstNodes = []
        lstLinks = []
        for strHost in lstHosts:
            newNode = Node(strHost)
            newNode.placeAtRandom(nMaxX, nMaxY)
            lstNodes.append(newNode)

        # Create links for each node
        for i in range(len(lstNodes)):
            lstDistances = []
            pNode        = lstNodes[i]

            # Calculate all distances
            for j in range(len(lstNodes)):
                # Elements are added to the list as a tuple (index, distance)
                # Where index is the relative to lstNodes
                if (j != i):
                    lstDistances.append((j, pNode.distanceTo(lstNodes[j])))

            # Order the list by distance (tuple field 1)
            lstDistances.sort(key=lambda x: x[1])
            # Select the N closest nodes and create the links
            for tupleNode in lstDistances[0:min(len(lstDistances), nNodeLinks)]:
                # Create the links
                destNode = lstNodes[tupleNode[0]]
                if (not TopologyGenerator.isLinkDuplicate(pNode, destNode, lstLinks)):
                    newLink = Link(pNode, lstNodes[tupleNode[0]])
                    lstLinks.append(newLink)
                    logging.debug('[createRandomTopo] New link orig=%s; dest=%s' % (newLink.origHost.Name(), newLink.destHost.Name()))

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
    def allNodesConnected(lstNodes, lstLinks):
        """
        Checks the given topology for islands of nodes that are not connected to all other nodes.
        """
        bDone             = False
        lstLinksCopy      = lstLinks.copy()
        curLink           = lstLinksCopy[0]
        lstConnectedNodes = [curLink.origHost, curLink.destHost]
        i                 = 0
        lstLinksCopy.remove(curLink)
        while(not bDone):

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

        # DEBUG - UNCONNECTED NODES LIST
        lstUnconnectedNodes = []
        for pNode in lstNodes:
            if (pNode not in lstConnectedNodes):
                lstUnconnectedNodes.append(pNode)

        # There is no link left to visit
        if (len(lstConnectedNodes) == len(lstNodes)):
            # All nodes have already been connected
            logging.info('[TopologyGenerator.allNodesConnected] All nodes are connected!')
            return True
        elif (len(lstLinksCopy) == 0):
            logging.error('[TopologyGenerator.allNodesConnected] Visited all links but could not reach all nodes, lstConnectedNodes=%s' % str(lstConnectedNodes))
            logging.error('[TopologyGenerator.allNodesConnected] Unconnected nodes=%s' % str(lstUnconnectedNodes))
            return False
        else:
            logging.error('[TopologyGenerator.allNodesConnected] Could not reach all nodes, lstConnectedNodes=%s' % str(lstConnectedNodes))
            logging.error('[TopologyGenerator.allNodesConnected] Unconnected nodes=%s' % str(lstUnconnectedNodes))
            return False

    @staticmethod
    def isLinkDuplicate(node1, node2, lstLinks):
        """
        Checks if a link with the same origin, destination nodes is already on the list. Links are bidirectional.
        """
        for pLink in lstLinks:
            if ((pLink.origHost == node1) and (pLink.destHost == node2)) or ((pLink.origHost == node2) and (pLink.destHost == node1)):
                return True
        return False

    @staticmethod
    def findLinkByNode(pNode, lstLinks):
        """
        Find link in lstLinks whose origin is pNode.
        """
        for pLink in lstLinks:
            if (pLink.origNode == pNode) or (pLink.destNode == pNode):
                return pLink
        return None
