"""
Generic functions used while setting up and running
producer/consumer experiments.

Created 12/10/2020 by Andre Dexheimer Carneiro
"""
from datetime import datetime

def curDatetimeToFloat():
    """
    Returns datetime as a float value
    """
    dtEpoch = datetime.utcfromtimestamp(0)
    dtNow   = datetime.now()
    return (dtNow - dtEpoch).total_seconds()

def floatToDatetime(sTime):
    """
    Return a datetime from a float time
    """
    return datetime.utcfromtimestamp(sTime)

def readHostNamesFromTopoFile(sTopoPath):
    """
    Returns a list containing the hostnames read from a MiniNDN topology file
    """
    c_strNodesTag    = '[nodes]'
    c_strLinksTag    = '[links]'
    c_strStationsTag = '[stations]'
    c_strApsTag      = '[accessPoints]'

    lstHosts = []
    with open(sTopoPath) as pFile:
        lstLines = pFile.readlines()

        bNodeSection = False
        for strLine in lstLines:
            # Begin the section where the hosts are described
            if (strLine.strip() == c_strNodesTag) or (strLine.strip() == c_strStationsTag):
                bNodeSection = True
                continue
            # Begin links session, end of the hosts session
            if (strLine.strip() == c_strLinksTag) or (strLine.strip() == c_strApsTag):
                bNodeSection = False
                continue              
            # Attempt to read hostnames which displays the following standard
            # b1: _ cache=0 radius=0.6 angle=3.64159265359
            if (bNodeSection):
                lstFields = strLine.split(':')

                if (len(lstFields) > 0) and (lstFields[0].strip() != ''):
                    lstHosts.append(lstFields[0])

    return lstHosts



