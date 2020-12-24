#!/usr/bin/python3
"""
draw_topology.py

Draws a topology read in the MiniNDN format.

22/12/2020        Andre Dexheimer Carneiro
"""
import sys
import logging
import matplotlib.pyplot as plt
from topology_generation import TopologyGenerator

c_strLogFile = '/home/andre/Source/icnsimulations/log/draw_topology.log'

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
    (lstNodes, lstLinks) = TopologyGenerator.readTopoFile(strTopoPath)

    #################################################
    # Draw individual nodes
    lstHumanCoord   = []
    lstSensorCoord  = []
    lstDroneCoord   = []
    lstVehicleCoord = []
    for pNode in lstNodes:
        if (pNode.getType() == 'human'):
            lstHumanCoord.append(pNode.getCoord())
        elif (pNode.getType() == 'sensor'):
            lstSensorCoord.append(pNode.getCoord())
        elif (pNode.getType() == 'drone'):
            lstDroneCoord.append(pNode.getCoord())
        elif (pNode.getType() == 'vehicle'):
            lstVehicleCoord.append(pNode.getCoord())

    # Draw points
    humanScatter = plt.scatter([x[0] for x in lstHumanCoord], [x[1] for x in lstHumanCoord], marker='*', s=120)
    sensorScatter = plt.scatter([x[0] for x in lstSensorCoord], [x[1] for x in lstSensorCoord], marker='x', s=120)
    droneScatter = plt.scatter([x[0] for x in lstDroneCoord], [x[1] for x in lstDroneCoord], marker='^', s=120)
    vehicleScatter = plt.scatter([x[0] for x in lstVehicleCoord], [x[1] for x in lstVehicleCoord], marker='s', s=120)

    # Draw hostnames
    for pNode in lstNodes:
        plt.annotate(pNode.Name(), (pNode.nX, pNode.nY), xytext=(pNode.nX+0.5, pNode.nY+0.5))

    # Draw legend
    plt.legend([humanScatter, sensorScatter, droneScatter, vehicleScatter], ['Soldado', 'Sensor', 'Drone', 'Veículo'], loc='upper right')

    #################################################
    # Draw links between nodes
    lstLinkCoords = []
    for pLink in lstLinks:
        lstLinkCoords = []
        lstLinkCoords.append(pLink.origHost.getCoord())
        lstLinkCoords.append(pLink.destHost.getCoord())
        plt.plot([x[0] for x in lstLinkCoords], [x[1] for x in lstLinkCoords], linewidth=1.5, zorder=-1)

    plt.show()
    logging.info('[main] Done! Log written to %s' % (c_strLogFile))

if __name__ == '__main__':
    main()