"""
node.py

Represents a node in the MiniNDN topology.

22/12/2020          Andre Dexheimer Carneiro
"""
import logging
import sys
import re
from random import randint
from math   import sqrt, atan, sin, cos

# ---------------------------------------------------------------------- Node
class Node:
    """
    Represents a Node element in the MiniNDN topology.
    """

    def __init__(self, strName, sRadius=-1, sAngle=-1):
        self.strName = strName
        self.sRadius = sRadius
        self.sAngle  = sAngle
        if (sRadius != -1) and (sAngle != -1):
            self.nX = int(round(cos(sAngle) * sRadius))
            self.nY = int(round(sin(sAngle) * sRadius))
        else:
            self.nX = -1
            self.nY = -1

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
            self.nX = randint(1, nMaxX)
            self.nY = randint(1, nMaxY)
            self.sRadius = sqrt(self.nX**2 + self.nY**2)
            self.sAngle  = atan(float(self.nY)/float(self.nX))
            logging.debug('[Node.placeAtRandom] host %s placed at x=%d; y=%d; r=%f; angle=%f' % (self.strName, self.nX, self.nY, self.sRadius, self.sAngle))

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
        strLine = '%s: _ radius=%f angle=%f' % (self.strName, self.sRadius, self.sAngle)
        return strLine

    def Name(self):
        return self.strName

    def getType(self):
        cType = self.strName[0]
        if (cType == 'h'):
            strType = 'human'
        elif (cType == 'd'):
            strType = 'drone'
        elif (cType == 's'):
            strType = 'sensor'
        elif (cType == 'v'):
            strType = 'vehicle'
        else:
            strType = 'other'

        return strType

    def getCoord(self):
        return (self.nX, self.nY)

    @staticmethod
    def fromString(strNode):
        """
        Returns a Node object read from conf file string.
        ex. b1: _ radius=0.6 angle=3.64159265359
        """
        sRadius = -1
        sAngle  = -1
        strName = ''
        newNode = None
        # Read host name
        lstContent = strNode.split(':')
        if (len(lstContent) > 0):
            strName = lstContent[0]
        # Read radius
        strRadiusRegex = r'.*radius=([0-9\.]+).*'
        pMatch = re.match(strRadiusRegex, strNode, re.M|re.I)
        if (pMatch):
            sRadius = float(pMatch.group(1))
        # Read angle
        strAngleRegex = r'.*angle=([0-9\.]+).*'
        pMatch = re.match(strAngleRegex, strNode, re.M|re.I)
        if (pMatch):
            sAngle = float(pMatch.group(1))

        if (strName != '') and (sRadius != -1) and (sAngle != -1):
            newNode = Node(strName, sRadius=sRadius, sAngle=sAngle)
            logging.debug('[Node.fromString] new Node name=%s, x=%d; y=%d; r=%f; angle=%s' % (newNode.Name(), newNode.nX, newNode.nY, newNode.sRadius, newNode.sAngle))

        return newNode

    @staticmethod
    def findByName(strName, lstNodes):
        """
        Returns a node with corresponding name from list
        """
        for pNode in lstNodes:
            if (pNode.strName == strName):
                return pNode
        return None