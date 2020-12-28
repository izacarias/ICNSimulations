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

from icnexperiment.result_analysis import readConsumerLogs

# Constants ----------------------------------------------------
c_strLogFile     = '/home/vagrant/icnsimulations/log/read_consumer_results.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# ---------------------------------------------------------------------- main
def main():
    # Log file location
    if (len(sys.argv) > 1):
        strPath = os.path.dirname(sys.argv[1])
    else:
        strPath = '/tmp/minindn'
    
    print('strPath=%s' % (strPath))

    readConsumerLogs(strPath)

if (__name__ == '__main__'):
    main()

