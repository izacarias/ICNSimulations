"""
Creates and manages Command And Control (C2) package types and
package queues.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import logging
import random

# ---------------------------------------- Constants
c_strAppName = 'C2Data'

# logging.basicConfig(filename="DataManager.log", format='%(asctime)s %(message)s', level=logging.DEBUG)

def main():

    logging.info('STARTING------------------------------------------')
    DataMgr = DataManager()

    lstHosts        = ['d1', 'd2', 'd3', 'h1']
    nMissionMinutes = 1
    lstDataQueue    = DataMgr.generateDataQueue(lstHosts, nMissionMinutes)

    nCount = 0
    for pNode in lstDataQueue:
        logging.info('%s ms, %s' % (pNode[0], pNode[1]))
        print('%s ms, %s' % (pNode[0], pNode[1]))
        nCount += 1
    print('Total data queue size: %s' %(nCount))


class DataManager:

    def __init__(self):
        """
        Constructor
        """
        self.lstDataTypes = []
        # Initialize known dataTypes
        self.lstDataTypes.append(C2DataType(nTTL=5000, nPeriod=20, nType=1, nSize=5000,
            lstAllowedHostTypes=['d', 'h', 'v', 's'], sRatioMaxReceivers=100, sPeriodWiggleRoom=0.2))   # INTEREST 1

    def generateDataQueue(self, lstHosts, nMissionMinutes):
        """
        Generates an unordered queue with packages and send time
        """
        lstDataQueue = []
        for strHost in lstHosts:
            # Generate data from each host
            # if(strHost[0] == 'd' and strHost[1] == '1'):
            if(strHost[0] == 'a'):
                # Drone
                logging.info('[generateDataQueue] Node type drone')
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[0].generateSpreadDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 'h'):
                # Human
                logging.info('[generateDataQueue] Node type human')
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 's'):
                # Sensor
                logging.info('[generateDataQueue] Node type sensor')
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 'v'):
                # Vehicle
                logging.info('[generateDataQueue] Node type vehicle')
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            else:
                # Unrecognized host type
                logging.error('[generateDataQueue] Unrecognized host type ' + strHost)

        lstDataQueue.sort(key=lambda x: x[0])
        return lstDataQueue

    def getTTLValuesParam(self):
        """
        Returns a string listing the TTL values for all available data types
        """
        strTTLValues = ''
        for DataType in self.lstDataTypes:
            strTTLValues += str(DataType.nTTL/1000) + ' '
        # Remove last whitespace
        strTTLValues = strTTLValues[:-1]
        return strTTLValues

class C2DataType:

    def __init__(self, nTTL, nPeriod, nType, nSize, lstAllowedHostTypes, sRatioMaxReceivers, sPeriodWiggleRoom):
        """
        Constructor
        """
        self.nTTL         = nTTL     # Time To Live in ms
        self.nPeriodSec   = nPeriod  # Creation period in s
        self.nType        = nType    # Type number
        self.nPayloadSize = nSize    # Package payload size
        self.nCurID       = 0        # Used for generating new packages

        self.sRatioMaxReceivers = sRatioMaxReceivers    # Ratio of possible receivers out of the receivers specified in the lstPossibleReceivers
        self.sPeriodWiggleRoom  = sPeriodWiggleRoom     # Ratio of acceptable period variation amongs sent packages

        self.lstAllowedHostTypes = lstAllowedHostTypes # Host types that can receive this data

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
            lstReceivers = self.getRandomDestHosts(lstPossibleReceivers)

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

        # lstDataQueue    = []
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
        strInterest = '/'+ c_strAppName + '/' + self.strOrig + '/C2Data-'
        strInterest = strInterest + str(self.nID) + '-Type' + str(self.nType)
        return strInterest

if (__name__ == '__main__'):
    main()
