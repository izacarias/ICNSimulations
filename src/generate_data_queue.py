#!/usr/bin/python
"""
This script generates the data queue use by ICN simulations.

Created 16/12/2020 by Andre Dexheimer Carneiro
"""
import sys
import pickle
import logging

from icnexperiment.data_generation import DataManager, readHostNamesFromTopoFile
from icnexperiment.dir_config import c_strLogDir

# ---------------------------------------- Constants
c_strLogFile         = c_strLogDir + 'generate_data_queue.log'
c_strTopologyFile    = '/home/vagrant/icnsimulations/topologies/default-topology.conf'
c_nMissionMinutes    = 40

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():
    """
    Generates a data queue saved with pickle which can be read by ICN experiments.
    The location of the pickle file is defined in DataManager and is set to the same directory as the topology file.
    """
    Manager = DataManager(nTotalReceivers=2)

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
    lstDataQueue = Manager.generateSpreadDataQueue(lstHostNames, c_nMissionMinutes)
    # lstDataQueue = Manager.generateDataQueue(lstHostNames, c_nMissionMinutes)

    # Log resulting data queue
    for nIndex, node in enumerate(lstDataQueue):
        logging.debug('[main] Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))

    # Store the resulting data queue using pickle
    # bStatus = DataManager.saveDataQueueToFile(lstDataQueue, strTopologyPath)
    DataManager.saveDataToTextFile(lstDataQueue, strTopologyPath)


    # if (not bStatus):
    #     logging.error('[main] Could not save data queue for topo file=' + strTopologyPath)

    logging.info('[main] Done!')

if __name__ == '__main__':
    main()
