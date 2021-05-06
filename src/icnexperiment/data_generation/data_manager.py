"""
Creates and manages Command And Control (C2) package types and
package queues.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import logging
import pickle
import subprocess
from os.path import dirname, basename, isfile

from .c2_datatype import C2DataType, DataPackage

# Constants --------------------------------
c_strTopoFileSuffix = '.conf'


class DataManager:

    def __init__(self):
        """
        Constructor
        """
        self.lstDataTypes = []
        nFactor           = 2
        # Initialize known dataTypes
        ################################################
        # Control data
        self.lstDataTypes.append(C2DataType(nTTL=10*1000/nFactor,   nPeriodSec=60/nFactor, nType=1, nSize=1024, sRatioMaxReceivers=1.0))   # INTEREST 1
        self.lstDataTypes.append(C2DataType(nTTL=1*60*1000/nFactor, nPeriodSec=60/nFactor, nType=2, nSize=1024*5, sRatioMaxReceivers=1.0))   # INTEREST 2
        ################################################
        # Operational data
        self.lstDataTypes.append(C2DataType(nTTL=2*60*1000/nFactor,  nPeriodSec=2*60/nFactor,  nType=3, nSize=1024*100, sRatioMaxReceivers=1.0))  # INTEREST 3
        self.lstDataTypes.append(C2DataType(nTTL=5*60*1000/nFactor,  nPeriodSec=5*60/nFactor,  nType=4, nSize=1024*1024*500, sRatioMaxReceivers=1.0))   # INTEREST 4
        self.lstDataTypes.append(C2DataType(nTTL=10*60*1000/nFactor, nPeriodSec=10*60/nFactor, nType=5, nSize=1024*1024*5, sRatioMaxReceivers=1.0))   # INTEREST 5
        self.lstDataTypes.append(C2DataType(nTTL=20*60*1000/nFactor, nPeriodSec=10*60/nFactor, nType=6, nSize=1024*1024*10, sRatioMaxReceivers=1.0))   # INTEREST 6

    def avgPayloadSize(self):
        nAvg = 0
        nSum = 0
        for pDataType in self.lstDataTypes:
            nSum += pDataType.nPayloadSize
        if (len(self.lstDataTypes) > 0):
            nAvg = nSum/len(self.lstDataTypes)
        else:
            nAvg = 0
        return nAvg

    def info(self):
        """
        Returns a multi-line string with information about all data types configured.
        """
        strInfo = ''
        for i in range(len(self.lstDataTypes)):
            strInfo += '[%d] - %s\n' % (i, self.lstDataTypes[i].toString())

        # Removes the last \n
        strInfo = strInfo[0:len(strInfo)]
        return strInfo

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

    def getTTLForDataType(self, nType):
        for pDataType in self.lstDataTypes:
            if (pDataType.nType == nType):
                return pDataType.nTTL
        raise Exception('Data type=%d does not exist' % nType)

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
    def createPayloadFiles(lstData, strBasePath):
        lstPayloads = DataManager.getPayloadSizesFromQueue(lstData)
        nFilesCreated = 0
        for nPayloadSize in lstPayloads:
            strFileName = DataManager.nameForPayloadFile(nPayloadSize, strBasePath)
            if (not isfile(strFileName)):
                strCmd = 'base64 /dev/urandom | head -c %d > %s' % (nPayloadSize, strFileName)
                subprocess.Popen(strCmd, shell=True)
                nFilesCreated += 1
                logging.info('[DataManager.createPayloadFiles] Created file with cmd=%s' % strCmd.split(' '))
        logging.info('[DataManager.createPayloadFiles] Created %d files' % nFilesCreated)

    @staticmethod
    def nameForPayloadFile(nPayloadSize, strBasePath):
        return strBasePath + '/' + 'file_' + str(int(nPayloadSize/1024)) + 'K'

    @staticmethod
    def saveDataQueueToFile(lstQueue, strTopoFilePath):
        """
        Stores a data queue using pickle
        """
        strPath = DataManager.pickleFileNameForFromTopo(strTopoFilePath)
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
        strPath  = DataManager.pickleFileNameForFromTopo(strTopoFilePath)
        lstQueue = None
        with open(strPath, 'rb') as pFile:
            logging.info('[DataManager.loadDataQueueFromFile] Reading data queue from path=%s' % strPath)
            lstQueue = pickle.load(pFile)
        return lstQueue

    @staticmethod
    def loadDataQueueFromTextFile(strTopoFilePath):
        """
        Loads data queue from txt file.
        """
        strPath  = DataManager.textFileNameForFromTopo(strTopoFilePath)
        lstData = list()
        with open(strPath, 'r') as pFile:
            lstLines = pFile.readlines()
            for strLine in lstLines:
                if (strLine.strip() != ''):
                    lstFields = strLine.split(';', 1)
                    nTimeMs = int(lstFields[0])
                    pPackage = DataPackage.fromTextLine(lstFields[1])
                    lstData.append([nTimeMs, pPackage])
        return lstData

    @staticmethod
    def saveDataToTextFile(lstData, strTopoFilePath):
        """
        Saves the data queue into a text file
        """
        strPath  = DataManager.textFileNameForFromTopo(strTopoFilePath)
        pFile = open(strPath, 'w')
        if (not pFile):
            logging.error('[DataManager.saveDataToTextFile] Error opening output file=%s' % strPath)
            return False
        
        for (nTime, pPackage) in lstData:
            strLine = '%d;%s\n' % (nTime, pPackage.toTextLine())
            pFile.write(strLine)

        logging.info('[DataManager.saveDataToTextFile] Saved %d packages' % len(lstData))        
        pFile.close()        

    @staticmethod
    def pickleFileNameForFromTopo(strTopoFilePath):
        """
        Returns the designated pickle file path
        """
        strTopoName = basename(strTopoFilePath)
        if (strTopoName.endswith('.conf')):
            strTopoName = strTopoName[:-5]

        strDirName = dirname(strTopoFilePath)
        if (strDirName != '') and (strDirName[-1] != '/'):
            strDirName += '/'
        
        strPath = strDirName + 'queue_' + strTopoName + '.pkl'
        return strPath

    @staticmethod
    def textFileNameForFromTopo(strTopoFilePath):
        """
        Returns the designated text file path
        """
        strTopoName = basename(strTopoFilePath)
        if (strTopoName.endswith('.conf')):
            strTopoName = strTopoName[:-5]

        strDirName = dirname(strTopoFilePath)
        if (strDirName != '') and (strDirName[-1] != '/'):
            strDirName += '/'
        
        strPath = strDirName + 'queue_' + strTopoName + '.txt'
        return strPath

    @staticmethod
    def getPayloadSizesFromQueue(lstData):
        lstPayloads = list()
        for (nTimestamp, pPackage) in lstData:
            if (pPackage.nPayloadSize not in lstPayloads):
                lstPayloads.append(pPackage.nPayloadSize)
        return lstPayloads