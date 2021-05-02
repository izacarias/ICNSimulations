#!/usr/bin/python3
"""
generate_topology

Custom topology generator. Returns MiniNDN readable .conf file for different topologies.

19/12/2020          Andre Dexheimer Carneiro
"""
import logging
import sys

from icnexperiment.topology_generation import TopologyGenerator
from icnexperiment.dir_config import c_strLogDir

# ---------------------------------------------------------------------- Constants
c_strLogFile = c_strLogDir + 'generate_topology.log'
c_nNodeLinks = 3
c_nSensors   = 2
c_nDrones    = 2
c_nHumans    = 2
c_nVehicles  = 2
c_nMaxX      = 10000
c_nMaxY      = 10000

"""
        20 40 60 80 100 nodes
Sensors  4 10 18 25  31
UAVs     8 14 22 25  38
Humans   6 12 16 25  25
Vehicles 2  4  4  5   6
"""

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def printUsage():
    logging.info('Usage: generate_topology.py <topoFile> <NDN>')

def main():

    bWifi = False    # By default, always generate wifi topology
    # Read command line parameter
    if (len(sys.argv) == 1):
        printUsage()
        exit()
    if (len(sys.argv) > 1):
        strTopologyPath = sys.argv[1]
    if (len(sys.argv) > 2) and (sys.argv[2].lower() == 'ndn'):
        bWifi = False

    logging.info('[main] Generating topology for nHumans=%d, nSensors=%s, nDrones=%d, nVehicles=%d' % (c_nHumans, c_nSensors, c_nDrones, c_nVehicles))

    # Create topology
    lstHosts = TopologyGenerator.createHostList(c_nHumans, c_nDrones, c_nSensors, c_nVehicles)

    # Wifi topologies instantiates an AP for each station, connecting all APs amongst themselves
    if (bWifi):
        pTopology = TopologyGenerator.createRandomTopoWifi(lstHosts, nNodeLinks=c_nNodeLinks, nMaxX=c_nMaxX, nMaxY=c_nMaxY)
    else:
        pTopology = TopologyGenerator.createRandomTopo(lstHosts, nNodeLinks=c_nNodeLinks, nMaxX=c_nMaxX, nMaxY=c_nMaxY)

    if (not pTopology.areAllNodesConnected()):
        logging.critical('[main] ATTENTION, NOT ALL NODES ARE CONNECTED!')

    pTopology.writeToFile(strTopologyPath)

    logging.info('[main] topology file written to path=%s' % strTopologyPath)

if __name__ == '__main__':
    main()
