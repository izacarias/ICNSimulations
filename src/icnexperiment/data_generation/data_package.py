"""
Data Package

Created 14/10/2020 by Andre Dexheimer Carneiro
"""

# ---------------------------------------- Constants
c_strAppName = 'C2Data'

class DataPackage:

    def __init__(self, nType, nID, nPayloadSize, strHost, strDest):
        """
        Constructor
        """
        self.nID          = nID
        self.nPayloadSize = nPayloadSize
        self.nType        = nType
        self.strOrig      = strHost
        self.strDest      = strDest

    def __repr__(self):
        """
        Repr
        """
        return '<DataPackage_Type%s_ID%s (%s -> %s)>' %(self.nType, self.nID, self.strOrig, self.strDest)

    def getInterest(self):
        """
        Returns the string representation of the interest filter
        """
        
        # strInterest = '/'+ c_strAppName + '/' + self.strOrig + '/C2Data-'
        # strInterest = strInterest + str(self.nID) + '-Type' + str(self.nType)

        # strInterest  = '/ndn/%s-site/%s' % (self.strOrig, self.strOrig)
        strInterest  = '/%s' % (self.strOrig)
        strInterest += '/C2Data-%d-Type%d' % (self.nID, self.nType)

        return strInterest
