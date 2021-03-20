#!/usr/bin/python3
"""
draw_topology.py

Draws a topology read in the MiniNDN format.

22/12/2020        Andre Dexheimer Carneiro
"""
import sys
import logging
import matplotlib.pyplot as plt

from icnexperiment.topology_generation import Topology
from icnexperiment.dir_config import c_strLogDir

c_strLogFile = c_strLogDir + 'draw_topology.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():

    # Read input param
    if (len(sys.argv) == 1):
        logging.error('[main] No topology specified as first parameter!')
        exit()
    else:
        strTopoPath = sys.argv[1]

    logging.info('[main] Drawing topology from path=%s' % strTopoPath)
    # (lstNodes, lstLinks) = TopologyGenerator.readTopoFile(strTopoPath)
    pTopology = Topology.loadFromFile(strTopoPath)

    #################################################
    # Draw individual nodes
    lstHumanCoord   = []
    lstSensorCoord  = []
    lstDroneCoord   = []
    lstVehicleCoord = []
    for pNode in pTopology.lstNodes:
        if (pNode.getType() == 'human'):
            lstHumanCoord.append(pNode.getCoord())
        elif (pNode.getType() == 'sensor'):
            lstSensorCoord.append(pNode.getCoord())
        elif (pNode.getType() == 'drone'):
            lstDroneCoord.append(pNode.getCoord())
        elif (pNode.getType() == 'vehicle'):
            lstVehicleCoord.append(pNode.getCoord())

    lstAccessCoord = []
    for pAP in pTopology.lstAccessPoints:
        lstAccessCoord.append(pAP.getCoord())

    # Draw points
    humanScatter   = plt.scatter([x[0] for x in lstHumanCoord], [x[1] for x in lstHumanCoord], marker='*', s=120)
    sensorScatter  = plt.scatter([x[0] for x in lstSensorCoord], [x[1] for x in lstSensorCoord], marker='x', s=120)
    droneScatter   = plt.scatter([x[0] for x in lstDroneCoord], [x[1] for x in lstDroneCoord], marker='^', s=120)
    vehicleScatter = plt.scatter([x[0] for x in lstVehicleCoord], [x[1] for x in lstVehicleCoord], marker='s', s=120)
    accessScatter  = plt.scatter([x[0] for x in lstAccessCoord], [x[1] for x in lstAccessCoord], c='k', marker='.', s=120)

    # Draw hostnames
    for pNode in pTopology.lstNodes:
        plt.annotate(pNode.Name(), (pNode.nX, pNode.nY), xytext=(pNode.nX+0.5, pNode.nY+0.5))

    # Draw legend
    lstScatters = [humanScatter, sensorScatter, droneScatter, vehicleScatter, accessScatter]
    lstLabels   = ['Soldado', 'Sensor', 'Drone', 'Veículo', 'AccessPoint']
    plt.legend(lstScatters, lstLabels, loc='upper right')

    #################################################
    # Draw links between nodes
    lstLinkCoords = []
    for pLink in pTopology.lstLinks:
        lstLinkCoords = []
        lstLinkCoords.append(pLink.origHost.getCoord())
        lstLinkCoords.append(pLink.destHost.getCoord())
        plt.plot([x[0] for x in lstLinkCoords], [x[1] for x in lstLinkCoords], linewidth=1.5, zorder=-1)

    ##################################################
    # Topology info
    logging.info('[main] Topology has links=%d; humans=%d; drones=%d; sensors=%d; vehicles=%d' % (len(pTopology.lstLinks), len(lstHumanCoord), len(lstDroneCoord), len(lstSensorCoord), len(lstVehicleCoord)))

    plt.show()
    logging.info('[main] Done! Log written to %s' % (c_strLogFile))

if __name__ == '__main__':
    main()