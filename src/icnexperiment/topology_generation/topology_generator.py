"""
topology_generator.py

Custom topology generator. Returns MiniNDN readable .conf file for different topologies.

22/12/2020          Andre Dexheimer Carneiro
"""
import logging
import sys
from .link import Link
from .node import Node, Station, AccessPoint
from .topology import Topology

# ---------------------------------------------------------------------- Constants
c_nDefaultNodeLinks = 5
c_strNodesTag       = '[nodes]'
c_strLinksTag       = '[links]'
c_nDefaultX         = 100
c_nDefaultY         = 100

class TopologyGenerator:
    """
    Handles MiniNDN readable topologies.
    """

    @staticmethod
    def createRandomTopo(lstHosts, nNodeLinks=c_nDefaultNodeLinks, nMaxX=c_nDefaultX, nMaxY=c_nDefaultY):
        """
        Places all hosts randomly in a X,Y space and stabilishes connections with the N hosts closest to each one.
        returns: Topology object containing lstStations and lstLinks
        """
        logging.info('[createRandomTopo] Begin maxX=%d, maxY=%d, NodeLinks=%d' % (nMaxX, nMaxY, nNodeLinks))
        # Place all nodes at random x,y coordinates
        lstStations = TopologyGenerator.placeStationsRandomly(lstHosts, nMaxX, nMaxY, Node)
        # Create links connecting each node
        lstLinks = TopologyGenerator.placeLinksBetweenNodes(lstStations, nNodeLinks)
        return Topology(lstStations, lstLinks)

    @staticmethod
    def createRandomTopoWifi(lstHosts, nNodeLinks=c_nDefaultNodeLinks, nMaxX=c_nDefaultX, nMaxY=c_nDefaultY):
        """
        Places hosts randomly in a X,Y space. Places AccessPoints directly next to hosts. Places links between
        the N closest AccessPoints.
        returns: Topology object containing lstStations, lstAccessPoints and lstLinks
        """
        logging.info('[createRandomTopoWifi] Begin maxX=%d, maxY=%d, NodeLinks=%d' % (nMaxX, nMaxY, nNodeLinks))
        # Place all nodes at random x,y coordinates
        lstStations = TopologyGenerator.placeStationsRandomly(lstHosts, nMaxX, nMaxY, Station)
        # Place access points connecting to each station
        lstAccessPoints = list()
        lstStationLinks = list()
        nCount = 0
        for pStation in lstStations:
            nCount += 1
            newAccessPoint = AccessPoint('ap%d' % nCount)
            newAccessPoint.place(pStation.nX, pStation.nY + 1)
            newLink = Link(pStation.strName, newAccessPoint.strName, nDelay=0, nBandwidth=0)
            lstStationLinks.append(newLink)
            # Might need to check for duplicate coordinates here
            lstAccessPoints.append(newAccessPoint)

        # Create links connecting each node
        lstApLinks = TopologyGenerator.placeLinksBetweenNodes(lstAccessPoints, nNodeLinks)
        logging.info('[TopologyGenerator.createRandomTopoWifi] lstStationLinks=%d, lstApLinks=%d' % (len(lstStationLinks), len(lstApLinks)))
        lstLinks = lstStationLinks + lstApLinks
        logging.info('[TopologyGenerator.createRandomTopoWifi] lstLinks=%d' % len(lstLinks))
        return Topology(lstStations, lstApLinks, lstAccessPoints)

    @staticmethod
    def placeStationsRandomly(lstHosts, nMaxX, nMaxY, NodeType):
        """
        Places stations randomly in a nMaxX by nMaxY area.
        """
        c_nMaxTriesForDuplicateCoord = 20
        lstStations = []
        for strHost in lstHosts:
            newStation      = NodeType(strHost)
            nTries          = 0
            bDuplicateCoord = False
            while bDuplicateCoord or (nTries == 0):
                #############################################
                # Nodes placed at the same point will cause
                # MiniNDN to raise an exception and quit
                nTries += 1
                bDuplicateCoord = False
                if (nTries > c_nMaxTriesForDuplicateCoord):
                    raise Exception('Tried more than %d times to find not duplicate coordinate' % c_nMaxTriesForDuplicateCoord)

                newStation.placeAtRandom(nMaxX, nMaxY)
                for pNode in lstStations:
                    if (newStation.getCoord() == pNode.getCoord()):
                        bDuplicateCoord = True

                if (not bDuplicateCoord):
                    lstStations.append(newStation)

        return lstStations

    @staticmethod
    def placeLinksBetweenNodes(lstNodes, nNodeLinks):

        lstLinks = []
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
                    logging.debug('placeLinksBetweenHosts New link orig=%s; dest=%s' % (newLink.origHost.Name(), newLink.destHost.Name()))

        return lstLinks

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
