"""
Generic functions used while setting up and running
producer/consumer experiments.

Created 12/10/2020 by Andre Dexheimer Carneiro
"""
import logging
from datetime import datetime

def getTimeSinceEpoch():
    """
    Returns time since epoch in ms as float
    """
    dtEpoch = datetime.utcfromtimestamp(0)
    dtNow   = datetime.now()
    return (dtNow - dtEpoch).total_seconds()*1000.0