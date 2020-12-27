"""
Creates and manages Command And Control (C2) package types and
package queues.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import logging
import pickle
from os.path import dirname, basename

from .c2_datatype import C2DataType

# Constants --------------------------------
c_strTopoFileSuffix = '.conf'


class DataManager:

    def __init__(self):
        """
        Constructor
        """
        self.lstDataTypes = []
        nFactor           = 10
        # Initialize known dataTypes
        ################################################
        # Control data
        self.lstDataTypes.append(C2DataType(nTTL=10*1000/nFactor,   nPeriodSec=60/nFactor, nType=1, nSize=5000, sRatioMaxReceivers=0.2))   # INTEREST 1
        self.lstDataTypes.append(C2DataType(nTTL=1*60*1000/nFactor, nPeriodSec=60/nFactor, nType=2, nSize=5000, sRatioMaxReceivers=0.2))   # INTEREST 2
        ################################################
        # Operational data
        self.lstDataTypes.append(C2DataType(nTTL=2*60*1000/nFactor,  nPeriodSec=2*60/nFactor,  nType=3, nSize=5000, sRatioMaxReceivers=0.4))   # INTEREST 3
        self.lstDataTypes.append(C2DataType(nTTL=5*60*1000/nFactor,  nPeriodSec=5*60/nFactor,  nType=4, nSize=5000, sRatioMaxReceivers=0.4))   # INTEREST 4
        self.lstDataTypes.append(C2DataType(nTTL=10*60*1000/nFactor, nPeriodSec=10*60/nFactor, nType=5, nSize=5000, sRatioMaxReceivers=0.4))   # INTEREST 5
        self.lstDataTypes.append(C2DataType(nTTL=20*60*1000/nFactor, nPeriodSec=20*60/nFactor, nType=6, nSize=5000, sRatioMaxReceivers=0.4))   # INTEREST 6

    def generateSpreadDataQueue(self, lstHosts, nMissionMinutes):
        """
        Generates a simple data queue for spreading packets from only one node.
        """
        lstDataQueue = []
        if (len(lstHosts) > 0):
            strHost = lstHosts[0]
            self.lstDataTypes[0].generateSpreadDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)

        return lstDataQueue

    def generateDataQueue(self, lstHosts, nMissionMinutes):
        """
        Generates an unordered queue with packages and send time
        """
        lstDataQueue = []
        for strHost in lstHosts:
            # Generate data from each host
            if(strHost[0] == 'd'):
                # Drone
                logging.info('[generateDataQueue] Node type drone, strHost=%s' % (strHost))
                self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[1].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[2].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[3].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[4].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[5].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 'h'):
                # Human
                logging.info('[generateDataQueue] Node type human, strHost=%s' % (strHost))
                self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[1].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[2].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[3].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[4].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[5].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 's'):
                # Sensor
                logging.info('[generateDataQueue] Node type sensor, strHost=%s' % (strHost))
                self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[1].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[2].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 'v'):
                # Vehicle
                logging.info('[generateDataQueue] Node type vehicle, strHost=%s' % (strHost))
                self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[1].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[2].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[3].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[4].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
                self.lstDataTypes[5].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            else:
                # Unrecognized host type
                logging.error('[generateDataQueue] Unrecognized host type ' + strHost)

        lstDataQueue.sort(key=lambda x: x[0])
        return lstDataQueue

    def getTTLValuesParam(self):
        """
        Returns a string listing the TTL values in ms for all available data types
        """
        strTTLValues = ''
        for DataType in self.lstDataTypes:
            strTTLValues += str(DataType.nTTL) + ' '
        # Remove last whitespace
        strTTLValues = strTTLValues[:-1]
        return strTTLValues

    def getPayloadValuesParam(self):
        """
        Returns a string listing the payload values for all available data types
        """
        strPayloadValues = ''
        for DataType in self.lstDataTypes:
            strPayloadValues += str(DataType.nPayloadSize) + ' '
        # Remove last whitespace
        strPayloadValues = strPayloadValues[:-1]
        return strPayloadValues

    @staticmethod
    def saveDataQueueToFile(lstQueue, strTopoFilePath):
        """
        Stores a data queue using pickle
        """
        strPath = DataManager.queueFileNameForFromTopo(strTopoFilePath)
        bResult = False
        with open(strPath, 'wb') as pFile:
            pickle.dump(lstQueue, pFile)
            bResult = True
            logging.info('[DataManager.saveDataQueueToFile] Data queue saved to path=%s' % strPath)
        return bResult

    @staticmethod
    def loadDataQueueFromFile(strTopoFilePath):
        """
        Loads a data queue using pickle
        """
        strPath  = DataManager.queueFileNameForFromTopo(strTopoFilePath)
        lstQueue = None
        with open(strPath, 'rb') as pFile:
            lstQueue = pickle.load(pFile)
        return lstQueue

    @staticmethod
    def queueFileNameForFromTopo(strTopoFilePath):
        """
        Returns the designated pickle file path
        """
        strPath = dirname(strTopoFilePath) + '/queue_' + basename(strTopoFilePath).strip(c_strTopoFileSuffix) + '.pkl'
        return strPath
