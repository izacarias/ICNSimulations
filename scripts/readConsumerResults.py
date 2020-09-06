"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        04/07/2020
"""
import os
import sys

# Constants
c_strFileName = 'consumerLog.log'


def readResultFile(File):
    """
    Reads the content of a result file
    """
    lstLines  = []
    for strLine in File:
        # Lines are in the format "%s;%.4f;%s", interest, timeDiff, result
        strLine = strLine.replace('\n', '')
        lstContents = strLine.split(';')
        if (len(lstContents) != 3):
            print('[readResultFile] line with more than 3 fields line=' + strLine)
        else:
            print('[readResultFile] (' + lstContents[0] + ', ' + lstContents[1] + ', ' + lstContents[2] + ')')
            lstLines.append(lstContents)

    return lstLines

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


