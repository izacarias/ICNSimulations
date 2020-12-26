#!/usr/bin/python
"""
This script generates the data queue use by ICN simulations.

Created 16/12/2020 by Andre Dexheimer Carneiro
"""
import sys
import pickle
import logging

from data_generation import DataManager, readHostNamesFromTopoFile

# ---------------------------------------- Constants
c_strLogFile         = '/home/vagrant/icnsimulations/log/generate_data_queue.log'
c_strTopologyFile    = '/home/vagrant/icnsimulations/topologies/default-topology.conf'
c_nMissionMinutes    = 5

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():
    """
    Generates a data queue saved with pickle which can be read by ICN experiments.
    The location of the pickle file is defined in DataManager and is set to the same directory as the topology file.
    """
    Manager = DataManager()

    # Read command line parameter
    if (len(sys.argv) == 1):
        logging.error('[main] no topology file specified. To use the default topology, use \'default\' as the first parameter')
        exit()
    elif (sys.argv[1] == 'default'):
        strTopologyPath = c_strTopologyFile
    else:
        strTopologyPath = sys.argv[1]

    # Read hostnames from the topology file and generate queue
    lstHostNames = readHostNamesFromTopoFile(strTopologyPath)
    logging.info('[main] Generating queue, missionMinutes= %d; hostnames=%s; topoFile=%s' % (c_nMissionMinutes, str(lstHostNames), strTopologyPath))
    lstDataQueue = Manager.generateDataQueue(lstHostNames, c_nMissionMinutes)

    # Log resulting data queue
    for nIndex, node in enumerate(lstDataQueue):
        logging.debug('[main] Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))

    # Store the resulting data queue using pickle
    bStatus = DataManager.saveDataQueueToFile(lstDataQueue, strTopologyPath)

    if (not bStatus):
        logging.error('[main] Could not save data queue for topo file=' + strTopologyPath)

    logging.info('[main] Done!')

if __name__ == '__main__':
    main()