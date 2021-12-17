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

from icnexperiment.data_generation import DataManager
from icnexperiment.result_analysis import *
from icnexperiment.dir_config import c_strLogDir

# Constants ----------------------------------------------------
c_strLogFile = c_strLogDir + 'read_consumer_results.log'



# ---------------------------------------------------------------------- main
def main():
    # Log file location

    logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    if (len(sys.argv) > 1):
        strTopoPath = sys.argv[1]
    else:
        logging.info('read_nfd_results.py <topofile>')
        exit(0)

    if (len(sys.argv) > 2):
        strPath = os.path.dirname(sys.argv[1])
    else:
        strPath = '/tmp/icnsimulations'

    readNfdResults(strTopoPath, strPath)

def readNfdResults(strTopoPath, strLogPath='/tmp/icnsimulations'):

    lstData = DataManager.loadDataQueueFromTextFile(strTopoPath)

    # Get hostnames from the data queue
    lstHostNames = []
    for [nTimestamp, pDataPackage] in lstData:
        if (pDataPackage.strOrig not in lstHostNames):
            lstHostNames.append(pDataPackage.strOrig)
        if (pDataPackage.strDest not in lstHostNames):
            lstHostNames.append(pDataPackage.strDest)

    hshNodes = readNFDLogs(strLogPath, lstData, lstHostNames)

    if (len(hshNodes) > 0):
        sAvgTransTime = avgTransTime(hshNodes)
        logging.info('[readNfdResults] Transmission time average=%f ms' % (sAvgTransTime))
    else:
        logging.info('[readNfdResults] No trasnmissions!')

if (__name__ == '__main__'):
    main()

