"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        04/07/2020
"""
import os
import sys
from datetime import datetime
from src.data_generation.generics import floatToDatetime

# Constants ----------------------------------------------------
c_strFileName = 'consumerLog.log'

class Transmission:

    def __init__(self, interest, timeDiff, info, timeSinceEpoch):
        self.strInterest     = interest
        self.sTimeDiff       = float(timeDiff)
        self.strInfo         = info
        self.dtDate          = floatToDatetime(float(timeSinceEpoch))
    
    def __repr__(self):
        return '<Transmission> interest=%s, timeDiff=%f, info=%s, timeSinceEpoch=%s' % (self.strInterest, 
            self.sTimeDiff, self.strInfo, self.dtDate)

def readResultFile(File):
    """
    Reads the content of a result file
    """
    lstTransmissions  = []
    for strLine in File:
        # Lines are in the format "%s;%.4f;%s;%.4%", interest, timeDiff, result, timeSinceEpoch
        strLine = strLine.replace('\n', '')
        lstContents = strLine.split(';')
        if (len(lstContents) != 4):
            print('[readResultFile] line with more or less than 4 fields line=' + strLine)
        else:
            newTrans = Transmission(lstContents[0], lstContents[1], lstContents[2], lstContents[3])
            print('[readResultFile] New Transmission=%s' % (newTrans))
            lstTransmissions.append(newTrans)

    return lstTransmissions

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
for strNode in lstNodes:
    # Read result file for each node
    strConsumerLog = strBasePath + '/' + strNode + '/' + c_strFileName
    if (os.path.exists(strConsumerLog)):
        pFile = open(strConsumerLog, 'r')
        if (pFile):
            print('[main] reading results for node=' + strNode)
            hshNodes[strNode] = readResultFile(pFile)
            pFile.close()
        else:
            print('[main] ERROR reading information for node=' + strNode)
    else:
        print('[main] could not find %s for node %s' % (c_strFileName, strNode))


