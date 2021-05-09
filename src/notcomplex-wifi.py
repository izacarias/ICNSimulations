#!/usr/bin/python

'This example creates a simple network topology with 1 AP and 2 stations'

import sys
import logging
import getopt
from process_topology import Topology
from icnexperiment.data_generation import DataManager
from icnexperiment.dir_config import c_strLogDir
from random_talks import RandomTalks
from read_nfd_results import readNfdResults

# Create logging
c_strLogFile = c_strLogDir + '/notcomplex-witi.log'
logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():

   bIsMock = False
   strMode = 'icn'
   strTopoPath = ''
   sCacheRatio = 1.0
   nIterations = 1

   short_options = 'hmt:'
   long_options  = ['help', 'mock', 'sdn', 'icn', 'ip', 'ip_sdn', 'icn_sdn', 'topo=', 'time=', 'cache-ratio=', 'iterations=']
   opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
   for opt, arg in opts:
      if opt in ['-h', '--help']:
         showHelp()
         exit(0)
      elif opt in ['-t', '--time']:
         nTimeSecs = int(arg)
      elif opt in '--topo':
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
      elif opt == '--cache-ratio':
         sCacheRatio = float(arg)
      elif opt == '--iterations':
         nIterations = int(arg)

   # Load data queue
   if (strTopoPath != ''):
      lstDataQueue = DataManager.loadDataQueueFromTextFile(strTopoPath)
      # lstDataQueue = list()
      logging.info('[main] Data queue size=%d' % len(lstDataQueue))
   else:
      logging.error('[main] No topology file specified!')
      showHelp()
      exit(0)

   # Setup and run experiment
   topo = Topology.fromFile(strTopoPath)
   topo.create(strMode=strMode, sCacheRatio=sCacheRatio)
   if (strMode == 'ip_sdn' or strMode == 'icn_sdn'):
      topo.net.pingAll(timeout='0.5s')

   nIterationsCompleted = 0
   while(nIterationsCompleted < nIterations):
      logging.info('[main] Begin experiment %d out of %d' % (nIterationsCompleted+1, nIterations))
      Experiment = RandomTalks(topo.net.stations, lstDataQueue)
      try:
         Experiment.setup()
         (dtBegin, dtEnd) = Experiment.run(nTimeSecs)
         nIterationsCompleted += 1

         # Read results
         readNfdResults(strTopoPath)

         # Clear everything stored in cache before next iteration
         topo.clearAllCache()
         topo.clearNfdLogs()
      except Exception as e:
         logging.error('[main] An exception was raised during the experiment: %s' % str(e))
         raise

   # topo.showCLI()
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