#!/usr/bin/python
"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        28/12/2020
"""
import sys
import logging
from os.path import dirname, exists
from os import listdir

from .transmission import Transmission

# Constants ----------------------------------------------------
c_strConsumerLog = 'consumerLog.log'

def readConsumerLogs(strPath):
    """
    Reads the consumer logs in each nodes' directory.
    Returns a dictionary containing the transmission list for each hostname.
    """
    # Save all directories as node names
    lstNodes = listdir(strPath)
    hshNodes = {}

    # Visit nodes (directories) one by one
    for strConsumer in lstNodes:
        # Read result file for each node
        strConsumerLog = strPath + '/' + strConsumer + '/' + c_strConsumerLog
        if (exists(strConsumerLog)):
            pFile = open(strConsumerLog, 'r')
            if (pFile):
                logging.info('[readConsumerLogs] reading results for node=%s ------------------------------------------' % (strConsumer))
                # Process each line for a transmission
                lstTransmissions  = []
                for strLine in pFile:
                    newTrans = Transmission.fromString(strLine, strConsumer)
                    lstTransmissions.append(newTrans)
                    logging.debug('[readConsumerLogs] Read new transmission=%s' % newTrans)

                hshNodes[strConsumer] = lstTransmissions
                pFile.close()
            else:
                logging.error('[readConsumerLogs] Error reading information for node=' + strConsumer)
        else:
            logging.info('[readConsumerLogs] could not find log=%s for node=%s' % (c_strConsumerLog, strConsumer))

# ---------------------------------------------------------------------- main
def main():
    # Read path from command line argument, if any
    if (len(sys.argv) > 1):
        strPath = dirname(sys.argv[1])
    else:
        strPath = '/tmp/minindn'
    
    logging.info('[main] Reading results from path=%s; fileName=%s' % (strPath, c_strConsumerLog))
    readConsumerLogs(strPath)

if (__name__ == '__main__'):
    main()