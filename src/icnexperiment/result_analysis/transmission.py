#!/usr/bin/python
"""
Represents a transmission between a producer and a consumer as read from the consumerLog file.

Andre Dexheimer Carneiro        28/12/2020
"""
import re

from icnexperiment.generics import floatToDatetime

class Transmission:

    def __init__(self, strConsumer, strInterest, delayUs, strStatus, timeSinceEpoch):
        self.strInterest = strInterest
        self.sDelayUs    = float(delayUs)
        self.dtDate      = floatToDatetime(float(timeSinceEpoch))
        self.strStatus   = strStatus
        self.strCons     = strConsumer
        self.strProd     = ''
        self.nDataID     = -1
        self.nDataType   = -1

        if (not self.processInterestFilter()):
            raise Exception('[Transmission.__init__] Could not read data from interest=%s' % self.strInterest)
    
    def __repr__(self):
        return '<Transmission> (%s -> %s) interest=%s, timeDiff=%f, status=%s, timeSinceEpoch=%s' % (self.strProd, self.strCons, self.strInterest, self.sDelayUs, self.strStatus, self.dtDate.strftime('%d/%m/%Y %H:%M:%S.%f'))
    
    def processInterestFilter(self):
        """
        Reads interest filter for origin host, destination host, data type and data ID.
        Interest filter format /C2Data/<strOrig>/C2Data-<ID>-Type<Type>.
        Returns True if data was successfully read.
        """
        strRegex = r'\/C2Data\/([a-zA-Z0-9]+)\/C2Data-([0-9]+)-Type([0-9]+)'
        pMatch = re.match(strRegex, self.strInterest)
        if (pMatch):
            self.strProd   = pMatch.group(1)
            self.nDataID   = int(pMatch.group(2))
            self.nDataType = int(pMatch.group(3))
            return True
        return False     
    
    @staticmethod
    def fromString(strLine, strConsumer):
        """
        Returns a Transmission object read from a consumerLog formatted line.
        The consumerLog format is "%s;%.4f;%s;%.4%", interest, timeDiff, result, timeSinceEpoch respectively
        """
        newTrans = None
        strLine  = strLine.replace('\n', '')
        lstContents = strLine.split(';')
        if (len(lstContents) == 4):
            newTrans = Transmission(strConsumer, lstContents[0], lstContents[1], lstContents[2], lstContents[3])
        else:
            raise Exception('[Transmission.fromString] Line with more or less than 4 fields line=%s' % strLine)
        return newTrans
