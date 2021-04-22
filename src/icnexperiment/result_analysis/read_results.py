#!/usr/bin/python
"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        28/12/2020
"""
import sys
import logging
from os.path import dirname, exists, isdir, isfile
from os import listdir

from .transmission import Transmission

# Constants ----------------------------------------------------
c_strConsumerLog = 'consumer.log'

def readConsumerLogs(strPath):
    """
    Reads the consumer logs in each nodes' directory.
    Returns a tuple containing the same Transmission objects organized in two distinct ways.
    (hshNodes, lstTransmissions) where hshNodes is a dictionary containing lists of transmissins per consumer name.
    """
    # Save all directories as node names
    lstNodes = listdir(strPath)
    lstTransmissions = list()
    hshNodes = {}

    # Visit nodes (directories) one by one
    for strConsumer in lstNodes:
        # Read result file for each node
        strHostDir = strPath + '/' + strConsumer
        if (isdir(strHostDir)):
            strConsumerLog = strHostDir + '/' + c_strConsumerLog
            if (exists(strConsumerLog) and isfile(strConsumerLog)):
                pFile = open(strConsumerLog, 'r')
                if (pFile):
                    logging.debug('[readConsumerLogs] reading results for node=%s ------------------------------------------' % (strConsumer))
                    # Process each line for a transmission
                    lstHostTransmissions  = []
                    for strLine in pFile:
                        newTrans = Transmission.fromString(strLine, strConsumer)
                        lstHostTransmissions.append(newTrans)
                        lstTransmissions.append(newTrans)
                        logging.debug('[readConsumerLogs] Read new transmission=%s' % newTrans)
                    
                    if (len(lstHostTransmissions) > 0):
                        hshNodes[strConsumer] = lstHostTransmissions
                    pFile.close()
                else:
                    logging.error('[readConsumerLogs] Error reading information for node=' + strConsumer)
            else:
                logging.error('[readConsumerLogs] could not find log=%s for node=%s' % (c_strConsumerLog, strConsumer))

    return (hshNodes, lstTransmissions)

def avgTransTime(hshNodes):
    """
    Returns the average transmission time in ms for all transmissions. Does not consider timeouts or nacks.
    """
    sTotalTimeMs = 0.0
    sAvgTime     = 0.0
    nTotalTrans  = 0
    for strNode in hshNodes:
        for pTrans in hshNodes[strNode]:
            if (pTrans.isData()):
                nTotalTrans  += 1
                sTotalTimeMs += pTrans.sDelayUs/1000.0
    
    # Calculate average
    if (nTotalTrans > 0):
        sAvgTime = sTotalTimeMs/nTotalTrans
    else:
        sAvgTime = 0
    logging.info('[avgTransTime] average=%s, transmissions=%d' % (sAvgTime, nTotalTrans))
    return sAvgTime

def stdDeviationTransTime(lstTransmissions, sAvg=-1):

    if (sAvg < 0):
        # Calculate average
        sDelaySum = 0.0
        nSamples  = 0
        for pTrans in lstTransmissions:
            if (pTrans.isData()):
                sDelaySum += pTrans.sDelayUs
                nSamples  += 1
        sAvg = 0.0
        if (nSamples > 0):
            sAvg = sDelaySum/nSamples
    
    # Calculate standard deviation



def avgTransTimePerType(hshNodes):
    """
    Returns a dic of the average transmission time in ms for each data type.
    """
    hshOcurrances = {}
    hshTimeSum    = {}
    for strNode in hshNodes:
        for pTrans in hshNodes[strNode]:
            if (pTrans.strStatus == 'DATA'):
                ########################################################################
                # Information is stored in hshNodes as a tupe (numOcurrances, sSum)
                if (pTrans.nDataType not in hshOcurrances):
                    hshOcurrances[pTrans.nDataType] = 0
                    hshTimeSum[pTrans.nDataType]    = 0.0

                hshOcurrances[pTrans.nDataType] += 1
                hshTimeSum[pTrans.nDataType]    += pTrans.sDelayUs/1000.0

    # Calculate averages for each type
    hshAverages = {}
    for nType in hshOcurrances:
        hshAverages[nType] = hshTimeSum[nType]/hshOcurrances[nType]
        logging.info('[avgTransPerType] type=%d; average=%s; transmissions=%d' % (nType, hshAverages[nType], hshOcurrances[nType]))

    return hshAverages

def countStatus(hshNodes):
    """
    Returns the number of DATAs, NACKs and TIMEOUTs in the form of a tuple (nDatas, nNacks, nTimeouts).
    """
    nDatas    = 0
    nNacks    = 0
    nTimeouts = 0
    for strNode in hshNodes:
        for pTrans in hshNodes[strNode]:
            if (pTrans.strStatus == 'DATA'):
                nDatas += 1
            elif (pTrans.strStatus == 'NACK'):
                nNacks += 1
            elif (pTrans.strStatus == 'TIMEOUT'):
                nTimeouts += 1
            else:
                raise Exception('[countStatus] Unreconized status=%s' % (pTrans.strStatus))
    return (nDatas, nNacks, nTimeouts)
