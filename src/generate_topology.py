"""
generate_topology

Custom topology generator. Returns MiniNDN readable .conf file for different topologies.

19/12/2020          Andre Dexheimer Carneiro
"""
import logging
import sys
from topology_generation import TopologyGenerator

# ---------------------------------------------------------------------- Constants
c_strDefaultTopoPath = '/home/vagrant/icnsimulations/topologies/default-test-topo.conf'
c_strLogFile     = '/home/vagrant/icnsimulations/log/generate_topology.log'
c_nNodeLinks     = 4
c_nHumans        = 10
c_nSensors       = 10 
c_nDrones        = 10
c_nVehicles      = 10

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

    # Create topology
    lstHosts = TopologyGenerator.createHostList(c_nHumans, c_nDrones, c_nSensors, c_nVehicles)
    (lstNodes, lstLinks) = TopologyGenerator.createRandomTopo(lstHosts, c_nNodeLinks)
    TopologyGenerator.writeTopoFile(lstNodes, lstLinks, strTopologyPath)

    logging.info('[main] topology file written to path=%s' % strTopologyPath)

if __name__ == '__main__':
    main()