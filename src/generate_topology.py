"""
generate_topology

Custom topology generator. Returns MiniNDN readable .conf file for different topologies.

19/12/2020          André Dexheimer Carneiro
"""
import logging
import sys
from random import randint
from math   import sqrt

c_strLogFile = 'E:/Source/icnsimulations/generate_topology.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

class Node:
    """
    Represents a Node element in the MiniNDN topology.
    """

    def __init__(self, strName):
        self.strName = strName
        self.nX      = -1
        self.nY      = -1

    def __eq__(self, other):
        return (type(self) == type(other)) and (self.strName == other.Name())

    def __repr__(self):
        return '<Node %s at (%d, %d)>' % (self.strName, self.nX, self.nY)

    def placeAtRandom(self, nMaxX, nMaxY):
        """
        Places the Node in a random pair of x,y coordinates
        """
        if (self.nX >= 0) or (self.nY >= 0):
            raise Exception('placeAtRandom: Node has already been placed at (%d ,%d)' % (self.nX, self.nY))
        else:
            self.nX = randint(0, nMaxX)
            self.nY = randint(0, nMaxY)

    def distanceTo(self, pNode):
        """
        Returns the distance to the given Node
        """
        sDistance = sqrt((pNode.nX - self.nX)**2 + (pNode.nY - self.nY)**2)
        if (sDistance < 0):
            raise Exception('distanceTo: distance between nodes %s and %s is less than zero' % (self.strName, pNode.strName))
        return sDistance

    def toTopoFile(self):
        """
        Returns Link string in MiniNDN topology file format
        ex. d1: _ radius=1 angle=4.71238898038
        """
        strLine = '%s: _' % (self.strName)
        return strLine

    def Name(self):
        return self.strName

class Link:
    """
    Represents a Link element in the MiniNDN topology.
    """

    c_nDefaultDelay     = 10
    c_nDefaultBandWidth = 1000
    c_nDefaultLoss      = 0

    def __init__(self, origHost, destHost, nDelay=c_nDefaultDelay, nBandwidth=c_nDefaultBandWidth, nLoss=c_nDefaultLoss):
        self.origHost   = origHost
        self.destHost   = destHost
        self.nDelay     = nDelay
        self.nBandwidth = nBandwidth
        self.nLoss      = nLoss

        if (self.origHost == self.destHost):
            raise Exception('Origin host is the same as destination')

    def __repr__(self):
        return '<Link %s->%s, delay=%dms>' % (self.origHost.Name(), self.destHost.Name(), self.nDelay)

    def toTopoFile(self):
        """
        Returns Link string in MiniNDN topology file format
        ex. a1:b1 delay=10ms bw=1000
        """
        strLine = '%s:%s delay=%dms bw=%d' % (self.origHost.Name(), self.destHost.Name(), self.nDelay, self.nBandwidth)
        if (self.nLoss >= 1):
            strLine += ' loss=%d' % self.nLoss
        return strLine

def createRandomTopo(lstHosts):
    """
    Places all hosts randomly in a X,Y space and stabilishes connections with the N hosts closest to each one.
    """
    c_nX = 100
    c_nY = 100
    c_nNodeLinks = 5
    logging.info('createRandomTopo: begin maxX=%d, maxY=%d, NodeLinks=%d' % (c_nX, c_nY, c_nNodeLinks))

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
        for tupleNode in lstDistances[0:min(len(lstDistances), c_nNodeLinks)]:
            # Create the links
            newLink = Link(pNode, lstNodes[tupleNode[0]])
            lstLinks.append(newLink)
            logging.debug('createRandomTopo: Node %s links to %s' % (newLink.origHost.Name(), newLink.destHost.Name()))

    return lstNodes, lstLinks

def writeTopoFile(lstNodes, lstLinks, strPath):

    c_strNodesTag = '[nodes]'
    c_strLinksTag = '[links]'

    with open(strPath, 'w') as pFile:
        pFile.write(c_strNodesTag + '\n')
        for pNode in lstNodes:
            pFile.write(pNode.toTopoFile() + '\n')
        pFile.write(c_strLinksTag + '\n')
        for pLink in lstLinks:
            pFile.write(pLink.toTopoFile() + '\n')

def createHostList(nHumans, nDrones, nSensors, nVehicles):
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

def main():
    lstHosts = createHostList(5, 5, 5, 5)
    (lstNodes, lstLinks) = createRandomTopo(lstHosts)
    writeTopoFile(lstNodes, lstLinks, 'E:/Source/icnsimulations/topologies/test-topo.conf')


if (__name__ == '__main__'):
    main()