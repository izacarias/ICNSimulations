#!/usr/bin/python3
"""
Reads the raw results written by MiniNDN consumers.

Andre Dexheimer Carneiro        04/07/2020
"""
import os
import sys
import logging
import re
from datetime import datetime

from icnexperiment.result_analysis import *
from icnexperiment.dir_config import c_strLogDir

# Constants ----------------------------------------------------
c_strLogFile = c_strLogDir + 'read_consumer_results.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# ---------------------------------------------------------------------- main
def main():
    # Log file location
    if (len(sys.argv) > 1):
        strPath = os.path.dirname(sys.argv[1])
    else:
        strPath = '/tmp/minindn'
    
    logging.info('[main] Reading consumer logs from path=%s' % (strPath))

    hshNodes = readConsumerLogs(strPath)

    if (len(hshNodes) > 0):

        lstNacks = []
        for strNode in hshNodes:
            for pTrans in hshNodes[strNode]:
                if (pTrans.strStatus == 'NACK'):
                    lstNacks.append(pTrans)

        lstNacks.sort(key=lambda x: x.dtDate)

        for pTrans in lstNacks:
            logging.debug('[main] NACK dtDate=%s (%s -> %s) nType=%d' % (pTrans.dtDate.strftime('%H:%M:%S.%f'), pTrans.strProd, pTrans.strCons, pTrans.nDataType))

        # Number of total datas, nacks and timeouts
        (nDatas, nNacks, nTimeouts) = countStatus(hshNodes)
        logging.info('[main] nDATA=%d; nNACK=%d; nTIMEOUT=%d' % (nDatas, nNacks, nTimeouts))

        # Average transmission time
        sAvgTransTime = avgTransTime(hshNodes)
        logging.info('[main] Transmission time average=%f ms' % (sAvgTransTime))

        # Average trasnmissiontime per type
        # hshTransTimes = avgTransTimePerType(hshNodes)
        # for nType in range(1, 7):
        #     if (nType in hshTransTimes):
        #         logging.info('[main] Transmission time for type=%d; average=%f ms' % (nType, hshTransTimes[nType]))

        # Basic info for each type
        hshTypes = basicInfoPerType(hshNodes)
        for nType in range(1, (min(7, len(hshNodes)+1))):
            if (nType in hshTypes):
                hshInfo = hshTypes[nType]
                print('[main] Info for type=%2d; nDATA=%5d; nNACK=%3d; nTIMEOUT=%3d; avgDelay=%.3f ms' % (nType, hshInfo['nDatas'], hshInfo['nNacks'], hshInfo['nTimeouts'], hshInfo['sDelayAvg']))
        
        # Log timeouts with date
        lstTimeouts = []
        lstTransmissions = []
        for strNode in hshNodes:
            for pTrans in hshNodes[strNode]:
                lstTransmissions.append(pTrans)
                if (pTrans.strStatus == 'TIMEOUT'):
                    lstTimeouts.append(pTrans)

        # lstTransmissions.sort(key=lambda x: x.dtDate)
        # for i in range(len(lstTransmissions)):
        #     pTrans = lstTransmissions[i]
        #     logging.info('[main] Transmission %d/%d - date=%s; status=%s; sDelay=%.3f; consumer=%s; producer=%s; interest=%s' % (i+1, len(lstTransmissions), pTrans.dtDate, pTrans.strStatus, pTrans.sDelayUs, pTrans.strCons, pTrans.strProd, pTrans.strInterest))
    else:
        logging.info('[main] No transmissions! lsn(hshNodes) = 0')

if (__name__ == '__main__'):
    main()

