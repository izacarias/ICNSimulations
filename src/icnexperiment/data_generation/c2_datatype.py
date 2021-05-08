"""
Command And Control (C2) package types.

Created 14/10/2020 by Andre Dexheimer Carneiro
"""
import random
import logging

from .data_package import DataPackage

class C2DataType:

    def __init__(self, nTTL, nPeriodSec, nType, nSize, sRatioMaxReceivers, sPeriodWiggleRoom=0.2, lstAllowedHostTypes=['d', 'h', 'v']):
        """
        Constructor
        """
        self.nTTL         = nTTL        # Time To Live in ms
        self.nPeriodSec   = nPeriodSec  # Creation period in s
        self.nType        = nType       # Type number
        self.nPayloadSize = nSize       # Package payload size
        self.nCurID       = 0           # Used for generating new packages

        self.sRatioMaxReceivers = sRatioMaxReceivers    # Ratio of possible receivers out of the receivers specified in the lstPossibleReceivers
        self.sPeriodWiggleRoom  = sPeriodWiggleRoom     # Ratio of acceptable period variation amongs sent packages

        self.lstAllowedHostTypes = lstAllowedHostTypes # Host types that can receive this data
        # By default, drones, humans and vehicles, sensors are left out because they are meant to only produce data and not consume it

    def toString(self):
        """
        Returns a string containing information about this datatype
        """
        strInfo = 'nType=%d; nTTL=%s; nPeriodSec=%d; nSize=%d; sRatioMaxReceivers=%f; sPeriodWiggleRoom=%s; lstAllowedHostTypes=%s' % (self.nType, self.nTTL, self.nPeriodSec, self.nPayloadSize, self.sRatioMaxReceivers, self.sPeriodWiggleRoom, self.lstAllowedHostTypes)
        return strInfo

    def generateDataQueue(self, strHost, nMissionMinutes, lstDataQueue, lstHosts):
        """
        Generates the data queue for a host
        """
        # Assemble list with possible receivers for this data type
        lstPossibleReceivers = self.generatePossibleReceiversList(strHost, lstHosts)

        # Assemble data queue
        nMissionSeconds = nMissionMinutes * 60
        nSecondsElapsed = 0
        nCount          = 0
        while (nSecondsElapsed <= nMissionSeconds):
            # Create data and add to list with miliseconds offset
            lstReceivers = self.getAllDestHosts(lstPossibleReceivers)

            # Iterate over the received list of receivers and their timestamps
            for pNode in lstReceivers:
                pData      = DataPackage(self.nType, self.nCurID, self.nPayloadSize, strHost, pNode[1])
                nTimestamp = (nSecondsElapsed*1000) + pNode[0]
                nCount    += 1
                lstDataQueue.append([nTimestamp, pData])

            self.nCurID    += 1
            nSecondsElapsed = nSecondsElapsed + self.nPeriodSec

        return nCount

    def generateSpreadDataQueue(self, strHost, nMissionMinutes, lstDataQueue, lstHosts):
        """
        Creates a a data queue of a single package to be sent to all hosts.
        """
        nReceiverIndex  = 0
        nSecondsElapsed = 0
        for nIndex in range(0, 100):
            nSecondsElapsed += 1
            if (nReceiverIndex < len(lstHosts)):
                strDest         = str(lstHosts[nReceiverIndex])
                nReceiverIndex += 1
                if(strDest != strHost):
                    pData      = DataPackage(self.nType, 1, self.nPayloadSize, strHost, strDest)
                    nTimestamp = (nSecondsElapsed*500)
                    lstDataQueue.append([nTimestamp, pData])
            else:
                nReceiverIndex = 0

    def generatePossibleReceiversList(self, strHost, lstHosts):
        """
        Generates a list with the indexes of all hosts that can receive this data type
        """
        lstPossibleReceivers = []
        for strNode in lstHosts:
            # Letter 0 defines the type of node(drone, human, sensor, vehicle)
            if((strNode[0] in self.lstAllowedHostTypes) and (strNode != strHost)):
                lstPossibleReceivers.append(strNode)

        if (len(lstPossibleReceivers) == 0):
            raise Exception('[C2DataTypes.generatePossibleReceiversList] ERROR, no available nodes for data type %s' % self.nType)
        else:
            return lstPossibleReceivers

    def getAllDestHosts(self, lstPossibleReceivers):
        """
        Returns list of receivers, containing all available consumers, and send timestamps (in ms) for new packages
        :rtype list of (int, str)
        """
        # Determine send timestamp for each receiver
        lstResult = []
        nPeriodMs = self.nPeriodSec*1000
        for strReceiver in lstPossibleReceivers:
            nTimetampMs = random.randint(nPeriodMs - nPeriodMs*self.sPeriodWiggleRoom, nPeriodMs + nPeriodMs*self.sPeriodWiggleRoom)
            lstResult.append((nTimetampMs, strReceiver))

        return lstResult

    def getRandomDestHosts(self, lstPossibleReceivers):
        """
        Returns a randomly generated list of receivers and send timestamps (in ms) for new packages
        :rtype list of (int, str)
        """
        if (self.sRatioMaxReceivers > 0):
            nMaxReceivers = int(self.sRatioMaxReceivers*len(lstPossibleReceivers))
            if (nMaxReceivers <= len(lstPossibleReceivers)):
                nReceivers = random.randint(1, nMaxReceivers)
            else:
                nReceivers = len(lstPossibleReceivers)
        else:
            nMaxReceivers = 1
            nReceivers    = 1

        lstReceivers  = []
        if (nReceivers <= len(lstPossibleReceivers)):
            # There is room to fit all
            while (len(lstReceivers) < nReceivers):
                nReceiver = random.randint(0, len(lstPossibleReceivers)-1)
                if (nReceiver not in lstReceivers):
                    lstReceivers.append(nReceiver)
        else:
            raise Exception('Length PossibleReceiversList (%s) is to short for nReceivers (%s) with sRatioMaxReceivers (%s)' %
                (len(lstPossibleReceivers), nReceivers, self.sRatioMaxReceivers))

        # Determine send timestamp for each receiver
        lstResult = []
        nPeriodMs = self.nPeriodSec*1000
        for nReceiver in lstReceivers:
            nTimetampMs = random.randint(nPeriodMs - nPeriodMs*self.sPeriodWiggleRoom, nPeriodMs + nPeriodMs*self.sPeriodWiggleRoom)
            lstResult.append((nTimetampMs, lstPossibleReceivers[nReceiver]))

        return lstResult

