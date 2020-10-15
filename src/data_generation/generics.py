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