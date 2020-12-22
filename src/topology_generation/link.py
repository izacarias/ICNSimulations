"""
link.py

Represents a link between nodes in the MiniNDN topology.

22/12/2020          Andre Dexheimer Carneiro
"""
import logging

# ---------------------------------------------------------------------- Link
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