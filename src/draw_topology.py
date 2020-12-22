"""
draw_topology.py

Draws a topology read in the MiniNDN format.

22/12/2020        Andre Dexheimer Carneiro
"""
import sys
import logging
# import matplotlib.pyplot as plt
from topology_generation import TopologyGenerator

c_strLogFile = '/home/vagrant/icnsimulations/log/draw_topology.log'

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():

    TopologyGenerator.readTopoFile('/home/vagrant/icnsimulations/topologies/test-topo.conf')    
    

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