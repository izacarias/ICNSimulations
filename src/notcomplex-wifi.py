#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys
import logging
from process_topology import Topology
from icnexperiment.dir_config import c_strLogDir

# Create logging
c_strLogFile = c_strLogDir + '/notcomplex-witi.log'
logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():
   strTopo = '/home/vagrant/icnsimulations/topologies/linear-topo3.conf'
   topo = Topology.fromFile(strTopo)
   topo.create()
   logging.info('[main] APs=%d; Stations=%d' % (len(topo.net.aps), len(topo.net.stations)))
   topo.showCLI()
   topo.destroy()

if (__name__ == '__main__'):
   main()