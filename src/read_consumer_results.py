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

from icnexperiment.result_analysis import readConsumerLogs, avgTransTime, avgTransTimePerType, countStatus
from icnexperiment.log_dir import c_strLogDir

# Constants ----------------------------------------------------
c_strLogFile = c_strLogDir + 'read_consumer_results.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
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

        # Number of datas, nacks and timeouts
        (nDatas, nNacks, nTimeouts) = countStatus(hshNodes)
        logging.info('[main] nDATA=%d; nNACK=%d; nTIMEOUT=%d' % (nDatas, nNacks, nTimeouts))

        # Average transmission time
        sAvgTransTime = avgTransTime(hshNodes)
        logging.info('[main] Transmission time average=%f ms' % (sAvgTransTime))

        # Average trasnmissiontime per type
        hshTransTimes = avgTransTimePerType(hshNodes)
        for nType in range(1, 6):
            logging.info('[main] Transmission time for type=%d; average=%f ms' % (nType, hshTransTimes[nType]))
    else:
        logging.info('[main] No transmissions! lsn(hshNodes) = 0')

if (__name__ == '__main__'):
    main()

