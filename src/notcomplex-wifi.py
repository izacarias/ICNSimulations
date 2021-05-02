#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys
import logging
import getopt
from process_topology import Topology
from icnexperiment.data_generation import DataManager
from icnexperiment.dir_config import c_strLogDir

# Create logging
c_strLogFile = c_strLogDir + '/notcomplex-witi.log'
logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():

   bIsMock = False
   strMode = 'icn'
   strTopoPath = ''

   short_options = 'hmt:'
   long_options  = ['help', 'mock', 'sdn', 'icn', 'ip', 'ip_sdn', 'icn_sdn', 'topology=']
   opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
   for opt, arg in opts:
      if opt in ['-h', '--help']:
         showHelp()
         exit(0)
      elif opt in ('-t', '--topology'):
         strTopoPath = arg
      elif opt in ['-m', '--mock']:
         bIsMock = True
      elif opt == '--sdn':
         strMode = 'sdn'
      elif opt == '--icn':
         strMode = 'icn'
      elif opt == '--ip':
         strMode = 'ip'
      elif opt == '--ip_sdn':
         strMode = 'ip_sdn'
      elif opt == '--icn_sdn':
         strMode = 'icn_sdn'

   # Load data queue
   # if (strTopoPath != ''):
   #    lstDataQueue = DataManager.loadDataQueueFromTextFile(strTopoPath)
   #    logging.info('[main] Data queue size=%d' % len(lstDataQueue))  
   # else:
   #    logging.error('[main] No topology file specified!')
   #    showHelp()
   #    exit(0)

   # Setup and run experiment
   topo = Topology.fromFile(strTopoPath)
   topo.create()
   topo.showCLI()
   topo.destroy()

def showHelp():
   strHelp  = 'Help: -----------------------------------------------\n'
   strHelp += 'Usage:\n'
   strHelp += './notcomplex-wifi.py -t <topology_path> <options>\n'
   strHelp += 'Options can be, in any order:\n'
   strHelp += '  --mock:   Runs mock experiment, without any calls to Mininet, MiniNDN, NFD, NLSR, ...\n'
   strHelp += '  --sdn:    SDN experiment with Ryu controller\n'
   strHelp += '  --icn:    ICN experiment without specific controller\n'
   strHelp += '  --ip:     IP experiment, no specific controller or cache\n'
   strHelp += '  --ip_sdn: IP with SDN experiment, with Ryu controller and no cache\n'
   print(strHelp)

if (__name__ == '__main__'):
   main()