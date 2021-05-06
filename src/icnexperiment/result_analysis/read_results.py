#!/usr/bin/python
"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        28/12/2020
"""
import sys
import logging
from os.path import dirname, exists, isdir, isfile
from os import listdir
import re

from .transmission import Transmission

# Constants ----------------------------------------------------
c_strConsumerLog = 'consumer.log'

def readNFDLogs(strBasePath, lstData, lstHostNames):
    
    # strBasePath contains the directories for each node
    lstDirs = listdir(strBasePath)
    hshNodes = {}

    for strHost in lstDirs:
        if (strHost in lstHostNames):
            strNfdPath = strBasePath + '/' + strHost + '/nfd.log'

            lstConsumerInterests = list()
            for (nTimestamp, pPackage) in lstData:
                if (pPackage.strDest == strHost):
                    lstConsumerInterests.append((pPackage.nType, pPackage.nID))

            lstTransmissions = readTrasmissionsForHost(strHost, strNfdPath, lstConsumerInterests)
            hshNodes[strHost] = lstTransmissions
            (nData, nNack, nTimeout) = countStatusForList(lstTransmissions)
            sAvg = avgTransTimeForList(lstTransmissions)
            logging.info('[readNFDLogs] Read %d transmissions for host=%s; DATA=%d; NACK=%d; avgDelay=%.2f ms' % (len(lstTransmissions), strHost, nData, nNack, sAvg/1000))

    return hshNodes

def avgTransTimeForList(lstTransmissions):
    sSum = 0.0
    nSamples = 0
    for pTrans in lstTransmissions:
        if (pTrans.isData()):
            nSamples += 1
            sSum += pTrans.sDelayUs
    if (nSamples > 0):
        sAvg = sSum/nSamples
    else:
        sAvg = 0
    return sAvg

def countStatusForList(lstTransmissions):
    nData = 0
    nNack = 0
    nTimeout = 0
    for pTrans in lstTransmissions:
        if (pTrans.isData()):
            nData += 1
        elif (pTrans.isNack()):
            nNack += 1
        elif (pTrans.isTimeout()):
            nTimeout += 1
    return (nData, nNack, nTimeout)

def readTrasmissionsForHost(strHost, strNfdPath, lstConsumedInterests):

    lstTransmissions = list()
    lstIncomingData  = list()
    lstIncomingNack  = list()
    lstOutgoingInterest = list()
    pFile = open(strNfdPath, 'r')
    if (pFile):
        lstLines = pFile.readlines()
        for strLine in lstLines:
            nPos = strLine.find('onIncomingData matching')
            if (nPos > 0):
                '''
                1619980266.382936 DEBUG: [nfd.Forwarder] onIncomingData matching=/localhost/nfd/rib/register/h7%07%1E%08%08localhop%08%03ndn%08%04nlsr%08%04sync%23%01%0Ai%02%01%17o%01%80j%01%0Al%01%02m%08%7F%FF%FF%FF%FF%FF%FF%FF/%00%00%01y.Y%2B%90/%EER%DD%85Jul%DC/%16%2B%1B%01%03%1C%26%07%24%08%09localhost%08%08operator%08%03KEY%08%08%11%F7%0DA%28%A0%93s/%17H0F%02%21%00%E6%C3%09%F9%2B%BB%CF-%AA%8C%D7%1E%B5_%0C%DB%9F%97%CC%E0%5EM%E3Yz%8C%0F%B6%FF%C4z%02%02%21%00%80%1D%01%00%0CC%9F%EC%CD%C5%9E%86%F7%C3%16G%5CL%3A%15%02%2Fp%09%90%17%AFTy%E0r%07
                '''
                sTimestamp = float(strLine.split('DEBUG')[0])
                strWord = 'matching='
                nPos = strLine.find(strWord)
                if (nPos > 0):
                    strFilter = strLine[nPos+len(strWord):].strip()
                    lstIncomingData.append([sTimestamp, strFilter, False]) 
                    # logging.info('[nfd] cons=%s IncomingData interest=%s, time=%.3f' % (strHost, strFilter, sTimestamp))
                else:
                    raise Exception('No %s in line=%s' % (strWord, strLine))
                continue

            nPos = strLine.find('onIncomingNack')
            if (nPos > 0):
                '''
                1619967955.552597 DEBUG: [nfd.Forwarder] onIncomingNack in=(278,0) nack=/ndn/h0-site/h0/Type1Id0/v=1619967955034/seg=1~None OK  
                '''
                sTimestamp = float(strLine.split('DEBUG')[0])
                strWord = 'nack='
                nPos = strLine.find(strWord)
                if (nPos > 0):
                    strFilter = strLine[nPos+len(strWord):].strip()
                    strWord = '~'
                    nPos = strFilter.find(strWord)
                    if (nPos > 0):
                        strFilter = strFilter[0:nPos].strip()
                    lstIncomingNack.append((sTimestamp, strFilter)) 
                    lstTransmissions.append(Transmission(strHost, strFilter, 0.0, 'NACK'))
                else:
                    raise Exception('No %s in line=%s' % (strWord, strLine))
                continue              
    
            nPos = strLine.find('onOutgoingInterest')
            if (nPos > 0):
                '''
                1619978727.726135 DEBUG: [nfd.Forwarder] onOutgoingInterest out=261 interest=/localhost/nfd/rib/register/h%27%07%12%08%03ndn%08%07s0-site%08%02s0i%02%01%17o%01%80j%01%14l%01%02m%04%007%15%90/%00%00%01y.A%B1%40/s%95s%FCO%0D~%03/%16%2B%1B%01%03%1C%26%07%24%08%09localhost%08%08operator%08%03KEY%08%08%11%F7%0DA%28%A0%93s/%17F0D%02%20d%A8%F8%FBvZ%13%3AJ%D8N%C3%DA%B4o%3C%D9b%EF%87%E1W%F3%00%EEP%E7s%ED%F2%90m%02%20%2BD%BC%28%81X%A2%1C%A8f.j%19_%9E%871%CDw%07R%F8%9B%8F%B4%AEv1r%FE%8E%C5
                '''
                sTimestamp = float(strLine.split('DEBUG')[0])
                strWord = 'interest='
                nPos = strLine.find(strWord)
                if (nPos > 0):
                    strFilter = strLine[nPos + len(strWord):].strip()
                    lstOutgoingInterest.append([sTimestamp, strFilter, False])
                    # logging.info('[nfd] cons=%s OutgoingInterest interest=%s, time=%.3f' % (strHost, strFilter, sTimestamp))
                else:
                    raise Exception('No %s in line=%s' % (strWord, strLine))
                continue
        pFile.close()  

    # logging.info('[readTransmissionsForHost] host=%s, nacks=%d' % (strHost, len(lstIncomingNack)))
    for [sEnd, strInterest, bDataEventUsed] in lstIncomingData:
        # logging.info('[nfd] cons=%s incoming data for interest=%s, at=%.2f' % (strHost, strInterest, sEnd))
        nLastIntIndex = -1
        pMatch = re.match('.+\/Type([0-9])Id([0-9]+)\/', strInterest)
        if (pMatch):
            nType = int(pMatch.group(1))
            nId   = int(pMatch.group(2))
            if ((nType, nId) in lstConsumedInterests):
                # Found consumed interest, calculate delay
                for nIndex in range(len(lstOutgoingInterest)):
                    # logging.info('interest=%s; interest2=%s' % (strInterest, strInterest2))
                    [sBegin, strInterest2, bUsed] = lstOutgoingInterest[nIndex]
                    if (strInterest == strInterest2) and (not bUsed):
                        if (sEnd >= sBegin):
                            # In case there are more than one interest for the received data, 
                            # consider only the one sent closest to the receive time
                            nLastIntIndex = nIndex

                            [sBegin, strInterest2, bUsed] = lstOutgoingInterest[nIndex]
                            sDelay = (sEnd - sBegin)*1000000 # Convert seconds to us
                            lstTransmissions.append(Transmission(strHost, strInterest, sDelay, 'DATA'))
                            # logging.info('strLineData=%s\nstrLineInterest=%s' % (strLineData, strLineInt))
                            # logging.info('[nfd] cons=%s match for interest=%s, sBegin=%.2f, sEnd=%.2f' % (strHost, strInterest, sBegin, sEnd))
                            lstOutgoingInterest[nIndex][2] = True
                            break
                
                
            # else:
            #     logging.info('[nfd] cons=%s not my data, filter=%s' % (strHost, strInterest))

    return lstTransmissions    

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
