#!/usr/bin/python
"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        04/07/2020
"""
import os
import sys
import logging
import re
from datetime import datetime

from data_generation.generics import floatToDatetime

# Constants ----------------------------------------------------
c_strFileName = 'consumerLog.log'
c_strLogFile  = '/home/vagrant/icnsimulations/log/read_consumer_results.log'
logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

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

def readResultFile(pFile, strConsumer):
    """
    Reads the content of a consumer log file.
    """
    lstTransmissions  = []
    for strLine in pFile:
        newTrans = Transmission.fromString(strLine, strConsumer)
        lstTransmissions.append(newTrans)
        logging.debug('[readResultFile] Read new transmission=%s' % newTrans)

    return lstTransmissions

# ---------------------------------------------------------------------- main
def main():
    # Log file location
    if (len(sys.argv) > 1):
        strBasePath = os.path.dirname(sys.argv[1])
        print('strBasePath=%s; strFileName=%s' % (strBasePath, c_strFileName))
    else:
        strBasePath = '/tmp/minindn'

    # Save all directories as node names
    lstNodes = os.listdir(strBasePath)
    hshNodes = {}

    # Visit nodes (directories) one by one
    for strConsumer in lstNodes:
        # Read result file for each node
        strConsumerLog = strBasePath + '/' + strConsumer + '/' + c_strFileName
        if (os.path.exists(strConsumerLog)):
            pFile = open(strConsumerLog, 'r')
            if (pFile):
                logging.info('[main] reading results for node=%s ------------------------------------------' % strConsumer)
                hshNodes[strConsumer] = readResultFile(pFile, strConsumer)
                pFile.close()
            else:
                print('[main] ERROR reading information for node=' + strConsumer)
        else:
            print('[main] could not find %s for node %s' % (c_strFileName, strConsumer))

if (__name__ == '__main__'):
    main()

