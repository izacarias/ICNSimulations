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

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():

    (lstNodes, lstLinks) = TopologyGenerator.readTopoFile('/home/andre/Source/icnsimulations/topologies/test-topo.conf')

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

    plt.scatter([x[0] for x in lstHumanCoord], [x[1] for x in lstHumanCoord], marker='*')
    plt.scatter([x[0] for x in lstSensorCoord], [x[1] for x in lstSensorCoord], marker='x')
    plt.scatter([x[0] for x in lstDroneCoord], [x[1] for x in lstDroneCoord], marker='^')
    plt.scatter([x[0] for x in lstVehicleCoord], [x[1] for x in lstVehicleCoord], marker='s')
    plt.show()

    '''
    point1 = [1, 2]
    point2 = [3, 4]
    x_values = [point1[0], point2[0]]
    # gather x-values
    y_values = [point1[1], point2[1]]
    # gather y-values
    plt.plot(x_values, y_values)

    # Fixing random state for reproducibility
    np.random.seed(19680801)

    x = np.random.rand(20)
    y = 1e7*np.random.rand(20)

    fig, ax = plt.subplots()
    ax.fmt_ydata = millions
    plt.plot(x, y, 'o')
    plt.show()
    '''


if __name__ == '__main__':
    main()