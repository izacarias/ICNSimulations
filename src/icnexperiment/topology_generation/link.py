"""
link.py

Represents a link between nodes in the MiniNDN topology.

22/12/2020          Andre Dexheimer Carneiro
"""
import logging
import re

from .node import Node

# ---------------------------------------------------------------------- Link
class Link:
    """
    Represents a Link element in the MiniNDN topology.
    """

    c_nDefaultDelay     = 10
    c_nDefaultBandWidth = 10
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

    @staticmethod
    def fromString(strLink, lstNodes):
        """
        Returns a Node object read from conf file string.
        ex. b1:d1 delay=500ms bw=1000 loss=12
        """
        origNode = None
        destNode = None
        strOrig  = ''
        strDest  = ''
        #####################################
        # Read host names
        strNamesRegex = r'([0-9a-zA-Z_]+):([0-9a-zA-Z_]+).*'
        pMatch = re.match(strNamesRegex, strLink, re.M)
        if (pMatch):
            strOrig = pMatch.group(1)
            strDest = pMatch.group(2)
        #####################################
        # Read delay
        nDelay        = -1
        strDelayRegex = r'.*delay=([0-9\.]+).*'
        pMatch = re.match(strDelayRegex, strLink, re.M|re.I)
        if (pMatch):
            nDelay = int(pMatch.group(1))
        #####################################
        # Read bandwidth
        nBandwidth = -1
        strBwRegex = r'.*bw=([0-9\.]+).*'
        pMatch = re.match(strBwRegex, strLink, re.M|re.I)
        if (pMatch):
            nBandwidth = int(pMatch.group(1))
        #####################################
        # Read loss
        nLoss        = -1
        strLossRegex = r'.*loss=([0-9\.]+).*'
        pMatch = re.match(strLossRegex, strLink, re.M|re.I)
        if (pMatch):
            nLoss = int(pMatch.group(1))

        logging.debug('[Link.fromString] origName=%s, destName=%s, delay=%d, bandwidth=%d, loss=%d' % (strOrig, strDest, nDelay, nBandwidth, nLoss))

        # Find origin and destination host names in the nodes list
        origNode = Node.findByName(strOrig, lstNodes)
        destNode = Node.findByName(strDest, lstNodes)

        # Create Link object to be returned
        if (origNode is not None) and (destNode is not None):
            newLink = Link(origNode, destNode, nDelay, nBandwidth, nLoss)
        else:
            newLink = None

        return newLink
