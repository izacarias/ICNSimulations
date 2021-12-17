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

"""
        10 20 30 40 60 80 100 nodes
Sensors  2  4  8 10 18 25  31
UAVs     4  8 12 14 22 25  38
Humans   3  6  9 12 16 25  25
Vehicles 1  2  1  4  4  5   6
"""

# Easying the number of nodes configuration
# Accept the number of nodes via command line arguments
"""
    nodes: [sensors, drones, humans, vehicles]
"""
c_conf = {
        10:  [ 2,  4,  3, 1],
        20:  [ 4,  8,  6, 2],
        30:  [ 8, 12,  9, 1],
        40:  [10, 14, 12, 4],
        60:  [18, 22, 16, 4],
        80:  [25, 25, 25, 5],
        100: [31, 38, 25, 6]
        }

# TODO:
    # Use sequential ap names (ap1, ap2, ap3, ...)
    # Create link between every host and their respective ap (dont forget argument _)
# ---------------------------------------------------------------------- Constants
c_strLogFile = c_strLogDir + 'generate_topology.log'
c_nNodeLinks = 3
c_nSensors   = 2
c_nDrones    = 4
c_nHumans    = 3
c_nVehicles  = 1
c_nMaxX      = 100000
c_nMaxY      = 100000

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def printUsage():
    logging.info('Usage: generate_topology.py <numberOfNodes in [10, 20, 30, 40, 60, 80, 100]> <topoFile> <NDN>')

def printErrorNodes():
    logging.info('Error: numberOfNodes should be a value form the following list: [10, 20, 30, 40, 60, 80, 100]')

def main():

    bWifi = True
    # Read command line parameter
    if (len(sys.argv) < 3):
        printUsage()
        exit()
    if (len(sys.argv) >= 3):
        totalNodes = int(sys.argv[1])
        if totalNodes not in c_conf.keys():
            printErrorNodes()
            exit()

        strTopologyPath = sys.argv[2]
        c_nSensors   = c_conf[totalNodes][0]
        c_nDrones    = c_conf[totalNodes][1]
        c_nHumans    = c_conf[totalNodes][2]
        c_nVehicles  = c_conf[totalNodes][3]
    if (len(sys.argv) >= 4  and (sys.argv[3].lower() == 'ndn')):
        bWifi = False

    logging.info('[main] Generating topology for nHumans=%d, nSensors=%s, nDrones=%d, nVehicles=%d' % (c_nHumans, c_nSensors, c_nDrones, c_nVehicles))

    # Create topology
    lstHosts = TopologyGenerator.createHostList(c_nHumans, c_nDrones, c_nSensors, c_nVehicles)

    # Wifi topologies instantiates an AP for each station, connecting all APs amongst themselves
    if (bWifi):
        pTopology = TopologyGenerator.createRandomTopoWifi(lstHosts, nNodeLinks=c_nNodeLinks, nMaxX=c_nMaxX, nMaxY=c_nMaxY)
    else:
        pTopology = TopologyGenerator.createRandomTopo(lstHosts, nNodeLinks=c_nNodeLinks, nMaxX=c_nMaxX, nMaxY=c_nMaxY)

    logging.info('[main] pTopology.lstLinks=%d' % len(pTopology.lstLinks))

    if (not pTopology.areAllNodesConnected()):
        logging.critical('[main] ATTENTION, NOT ALL NODES ARE CONNECTED!')

    pTopology.writeToFile(strTopologyPath)

    logging.info('[main] topology file written to path=%s' % strTopologyPath)

if __name__ == '__main__':
    main()
