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
c_strDefaultTopoPath = '/home/vagrant/icnsimulations/topologies/default-test-topo.conf'
c_strLogFile         = c_strLogDir + 'generate_topology.log'
c_nNodeLinks         = 3
c_nHumans            = 7
c_nSensors           = 7
c_nDrones            = 7
c_nVehicles          = 7
c_nMaxX              = 100
c_nMaxY              = 100

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():

    # Read command line parameter
    if (len(sys.argv) == 1):
        logging.error('[main] no topology file specified. To use default, use \'default\' as the first parameter')
        exit()
    elif (sys.argv[1] == 'default'):
        strTopologyPath = c_strDefaultTopoPath
    else:
        strTopologyPath = sys.argv[1]

    logging.info('[main] Generating topology for nHumans=%d, nSensors=%s, nDrones=%d, nVehicles=%d' % (c_nHumans, c_nSensors, c_nDrones, c_nVehicles))

    # Create topology
    lstHosts = TopologyGenerator.createHostList(c_nHumans, c_nDrones, c_nSensors, c_nVehicles)
    (lstNodes, lstLinks) = TopologyGenerator.createRandomTopo(lstHosts, nNodeLinks=c_nNodeLinks, nMaxX=c_nMaxX, nMaxY=c_nMaxY)
    if (not TopologyGenerator.allNodesConnected(lstNodes, lstLinks)):
        logging.critical('[main] ATTENTION, NOT ALL NODES ARE CONNECTED!')

    TopologyGenerator.writeTopoFile(lstNodes, lstLinks, strTopologyPath)

    logging.info('[main] topology file written to path=%s' % strTopologyPath)

if __name__ == '__main__':
    main()
