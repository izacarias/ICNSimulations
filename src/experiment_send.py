#!/usr/bin/python
"""
This MiniNDN experiment instantiates consumers and producers based on the
packages and their timestamps created and queued by DataManager.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import sys
import time
import logging
import getopt
from random   import randint
from datetime import datetime, timedelta

try:
   from mininet.log import setLogLevel, info
   from minindn.minindn import Minindn
   from minindn.util import MiniNDNCLI
   from minindn.apps.app_manager import AppManager
   from minindn.apps.nfd import Nfd
   from minindn.apps.nlsr import Nlsr
   from mininet.node import Ryu
   g_bMinindnLibsImported = True
except ImportError:
   print('Could not import MiniNDN libraries')
   g_bMinindnLibsImported = False

from icnexperiment.data_generation import DataManager, curDatetimeToFloat, readHostNamesFromTopoFile
from icnexperiment.dir_config import c_strLogDir, c_strTopologyDir

# ---------------------------------------- Constants
c_strAppName         = 'C2Data'
c_strLogFile         = c_strLogDir + 'experiment_send.log'
c_strTopologyFile    = c_strTopologyDir + 'default-topology.conf'

c_nSleepThresholdMs  = 100
c_sExperimentTimeSec = 2*60

c_nCacheSizeDefault = 65536

c_nNLSRSleepSec   = 40
c_strNLSRLogLevel = 'NONE'
c_strNFDLogLevel  = 'NONE'

g_bIsMockExperiment  = False
g_bExperimentModeSet = False
g_bSDNEnabled        = False
g_strNetworkType     = ''

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


# ---------------------------------------- RandomTalks
class RandomTalks():

   def __init__(self, lstHosts):
      """
      Constructor. Meh
      """
      self.logFile      = None
      self.pDataManager = DataManager()
      self.lstHosts     = lstHosts

   def setup(self, strTopoPath):
      """
      Setup experiment
      """
      logging.info('[RandomTalks.setup] Setting up new experiment')

      # Load data queue
      self.lstDataQueue = DataManager.loadDataQueueFromFile(strTopoPath)
      logging.info('[RandomTalks.setup] Data queue size=%d' % len(self.lstDataQueue))

      # Get TTLs from data manager
      strTTLValues = self.pDataManager.getTTLValuesParam()
      strPayloadValues = self.pDataManager.getPayloadValuesParam()

      # Instantiate all producers
      for pHost in self.lstHosts:
         self.instantiateProducer(pHost, strTTLValues, strPayloadValues)

      # Log resulting data queue
      for nIndex, node in enumerate(self.lstDataQueue):
         logging.debug('[RandomTalks.setup] Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))

      # Log the current configuration for data_manager
      logging.info('[RandomTalks.setup] Current data type configuration: \n%s' % self.pDataManager.info())
      logging.info('[RandomTalks.setup] Note that this could be outdated since the data queue configuration is set when it is created!')

   def run(self):
      """
      Experiment routine
      """
      logging.info('[RandomTalks.run] Begin, maxExperimentTimeSec=%f' % c_sExperimentTimeSec)

      # Internal parameters
      dtInitialTime  = datetime.now()
      dtCurTime      = None
      dtDelta        = timedelta()
      nDataIndex     = 0
      sElapsedTimeMs = 0
      nIteration     = 0
      while (((sElapsedTimeMs/1000) < c_sExperimentTimeSec) and (nDataIndex < len(self.lstDataQueue))):
         # Send data until the end of the experiment time
         # Sweep queue and send data according to the elapsed time
         dtCurTime      = datetime.now()
         dtDelta        = dtCurTime - dtInitialTime
         sElapsedTimeMs = dtDelta.microseconds/1000 + dtDelta.seconds*1000
         nIteration    += 1
         logging.debug('[RandomTalks.run] New iteration with sElapsedTimeMs=%s; dtDelta=%s' % (sElapsedTimeMs, str(dtDelta)))

         while (nDataIndex < len(self.lstDataQueue)) and (self.lstDataQueue[nDataIndex][0] <= sElapsedTimeMs):
            # Send data
            pDataBuff = self.lstDataQueue[nDataIndex]
            logging.info('[RandomTalks.run] About to send data nDataIndex=%d/%d; pDataBuff[0]=%s; sElapsedTimeMs=%s' % (nDataIndex, len(self.lstDataQueue)-1, pDataBuff[0], sElapsedTimeMs))
            self.instantiateConsumer(pDataBuff[1])
            nDataIndex += 1

         if (nDataIndex < len(self.lstDataQueue)):
            logging.debug('[RandomTalks.run] Waiting to send next data package nDataIndex=%s; pDataBuff[0]=%s; sElapsedTimeMs=%s' %
               (nDataIndex, self.lstDataQueue[nDataIndex][0], sElapsedTimeMs))
         else:
            logging.info('[RandomTalks.run] No more data to send')

         # Wait until next data is ready, if past threshold
         if (nDataIndex < len(self.lstDataQueue)):
            nNextStopMs = self.lstDataQueue[nDataIndex][0] - sElapsedTimeMs
            if (nNextStopMs > c_nSleepThresholdMs):
               logging.info('[RandomTalks.run] Sleeping until next data nNextStopMs=%s; c_nSleepThresholdMs=%s' % (nNextStopMs, c_nSleepThresholdMs))
               time.sleep(nNextStopMs/1000.0)

      # Close log file
      logging.info('[RandomTalks.run] Experiment done in %s seconds log written to %s' % (sElapsedTimeMs/1000, c_strLogFile))

   def instantiateConsumer(self, pDataPackage):
      """
      Issues MiniNDN commands to set up a consumer for a data package
      """
      # Find consumer associated to the package
      nConsumer = self.findHostIndexByName(pDataPackage.strDest)

      if(nConsumer >= 0):
         # Valid consumer and producer
         pConsumer   = self.lstHosts[nConsumer]
         strInterest = pDataPackage.getInterest()
         sTimestamp  = curDatetimeToFloat()
         strCmdConsumer = 'consumer %s %s %f &' % (strInterest, str(pConsumer), sTimestamp)
         pConsumer.cmd(strCmdConsumer)
         logging.debug('[RandomTalks.instantiateConsumer] ConsumerCmd: ' + strCmdConsumer)
      else:
         raise Exception('[RandomTalks.instantiateConsumer] ERROR, invalid origin host in data package=%s' % pDataPackage)

   def instantiateProducer(self, pHost, strTTLValues, strPayloadValues):
      """
      Issues MiniNDN commands to instantiate a producer
      """
      ############################################################################
      # The experiment uses the default advertisements estabilished by NLSR, these advertisements were found lowering
      # NLSR log level to debug. Previously, advertise commands were issued in each producer, however this would cause
      # a bunch of NACKs were the should not be.
      # strCmdAdvertise = 'nlsrc advertise %s' % strFilter
      # pHost.cmd(strCmdAdvertise)
      # logging.debug('[RandomTalks.instantiateProducer] AdvertiseCmd: ' + strCmdAdvertise)

      strFilter      = self.getFilterByHostname(str(pHost))
      strCmdProducer = 'producer %s %s %s &' % (strFilter, strTTLValues, strPayloadValues)
      pHost.cmd(strCmdProducer)
      logging.debug('[RandomTalks.instantiateProducer] Instantiating new producer ' + str(pHost) + ' ' + strFilter + ' &')
      logging.debug('[RandomTalks.instantiateProducer] ProducerCmd: ' + strCmdProducer)

   def findHostIndexByName(self, strName):
      """
      Finds a host in MiniNDN self.lstHosts by name
      """
      for (nIndex, pNode) in enumerate(self.lstHosts):
         if (str(pNode) == strName):
            return nIndex
      return -1

   def getFilterByHostname(self, strName):
      """
      Creates interest filter base on the producer`s name
      """
      # return '/' + c_strAppName + '/' + strName + '/'
      return '/ndn/%s-site/%s/' % (strName, strName)

# ---------------------------------------- MockHost
class MockHost():

   def __init__(self, strName):
      # Shit
      self.strName = strName

   def __repr__(self):
      return self.strName

   def cmd(self, strLine):
      return 0

# ---------------------------------------- runMock
def runMock(strTopoPath):
   """
   Runs mock experiment. No cummunication with Mininet or MiniNDN
   """
   logging.info('[runMock] Running mock experiment')
   lstHostNames = readHostNamesFromTopoFile(strTopoPath)
   lstHosts = [MockHost(strName) for strName in lstHostNames]
   Experiment = RandomTalks(lstHosts)
   Experiment.setup(strTopoPath)
   Experiment.run()

# ---------------------------------------- runExperiment
def runExperiment(strTopoPath):
   """
   Runs experiment
   """
   logging.info('[runExperiment] Running MiniNDN experiment')
   setLogLevel('info')
   Minindn.cleanUp()
   Minindn.verifyDependencies()

   ######################################################
   # Start MiniNDN and set controller, if any
   if (g_bSDNEnabled):
      ndn = Minindn(topoFile=strTopoPath, controller=Ryu)
   else:
      ndn = Minindn(topoFile=strTopoPath)
   ndn.start()

   #######################################################
   # Initialize NFD and set cache size based on host type
   info('Starting NFD on nodes\n')
   lstHumanHosts   = []
   lstDroneHosts   = []
   lstSensorHosts  = []
   lstVehicleHosts = []
   for pHost in ndn.net.hosts:
      if (pHost.name[0] == 'h'):
         lstHumanHosts.append(pHost)
      elif (pHost.name[0] == 'd'):
         lstDroneHosts.append(pHost)
      elif (pHost.name[0] == 's'):
         lstSensorHosts.append(pHost)
      elif (pHost.name[0] == 'v'):
         lstVehicleHosts.append(pHost)
      else:
         raise Exception('[runExperiment] Hostname=%s not recognized as human, drone, sensor or vehicle' % pHost.name)

   nfdsHuman = AppManager(ndn, lstHumanHosts, Nfd, csSize=c_nHumanCacheSize, logLevel=c_strNFDLogLevel)
   info('[runExperiment] Cache set for humans=%d, size=%d\n' % (len(lstHumanHosts), c_nHumanCacheSize))
   nfdsDrone = AppManager(ndn, lstDroneHosts, Nfd, csSize=c_nDroneCacheSize, logLevel=c_strNFDLogLevel)
   info('[runExperiment] Cache set for drones=%d, size=%d\n' % (len(lstDroneHosts), c_nDroneCacheSize))
   nfdsSensor = AppManager(ndn, lstSensorHosts, Nfd, csSize=c_nSensorCacheSize, logLevel=c_strNFDLogLevel)
   info('[runExperiment] Cache set for sensors=%d, size=%d\n' % (len(lstSensorHosts), c_nSensorCacheSize))
   nfdsVehicle = AppManager(ndn, lstVehicleHosts, Nfd, csSize=c_nVehicleCacheSize, logLevel=c_strNFDLogLevel)
   info('[runExperiment] Cache set for vehicles=%d, size=%d\n' % (len(lstVehicleHosts), c_nVehicleCacheSize))

   ##########################################################
   # Initialize NFD
   info('Starting NLSR on nodes\n')
   nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr, logLevel=c_strNLSRLogLevel)

   ##########################################################
   # Wait for NLSR initialization, at least 30 seconds to be on the safe side
   logging.info('[runExperiment] NLSR sleep set to %d seconds' % c_nNLSRSleepSec)
   time.sleep(c_nNLSRSleepSec)

   ##########################################################
   # Set up and run experiment
   Experiment = RandomTalks(ndn.net.hosts)
   Experiment.setup(strTopoPath)
   Experiment.run()

   # MiniNDNCLI(ndn.net)
   ndn.stop()

# ---------------------------------------- setICNCache
def setICNCache():
   """
   Sets cache for ICN hosts.
   """
   global c_nHumanCacheSize, c_nDroneCacheSize, c_nSensorCacheSize, c_nVehicleCacheSize
   c_nHumanCacheSize   = c_nCacheSizeDefault
   c_nDroneCacheSize   = c_nCacheSizeDefault
   c_nSensorCacheSize  = c_nCacheSizeDefault
   c_nVehicleCacheSize = c_nCacheSizeDefault
   logging.info('[setICNCache] Set, human=%d, drone=%d, sensor=%d, vehicle=%d' % (c_nHumanCacheSize, c_nDroneCacheSize, c_nSensorCacheSize, c_nVehicleCacheSize))

# ---------------------------------------- setIPCache
def setIPCache():
   """
   Sets cache for IP hosts.
   """
   global c_nHumanCacheSize, c_nDroneCacheSize, c_nSensorCacheSize, c_nVehicleCacheSize
   c_nHumanCacheSize   = 0
   c_nDroneCacheSize   = 0
   c_nSensorCacheSize  = 0
   c_nVehicleCacheSize = 0
   logging.info('[setIPCache] Set, human=%d, drone=%d, sensor=%d, vehicle=%d' % (c_nHumanCacheSize, c_nDroneCacheSize, c_nSensorCacheSize, c_nVehicleCacheSize))

# ---------------------------------------- setNetworkType
def setNetworkType(strMode):
   """
   Sets the network as 'sdn', 'icn' or 'ip'
   """
   global g_strNetworkType, g_bSDNEnabled
   if (g_strNetworkType == ''):
      if (strMode == 'sdn'):
         g_bSDNEnabled = True
         setICNCache()
      elif (strMode == 'icn'):
         g_bSDNEnabled = False
         setICNCache()
      elif (strMode == 'ip'):
         g_bSDNEnabled = False
         setIPCache()
      elif (strMode == 'ip_sdn'):
         g_bSDNEnabled = True
         setIPCache()
      else:
         raise Exception('[setNetworkType] Unrecognized network type=%s' % strMode)

      g_strNetworkType = strMode
      logging.info('[setNetworkType] Type=%s, RyuController=%s' % (g_strNetworkType, g_bSDNEnabled))
   else:
      raise Exception('[setNetworkType] called more than once, current type=%s' % g_strNetworkType)

# ---------------------------------------- showHelp
def showHelp():
   strHelp  =  'Help: -----------------------------------------------\n'
   strHelp += 'experiment_send.py - runs MiniNDN experiments with C2Data\n\n'
   strHelp += 'Usage:\n'
   strHelp += './experiment_send.py -t <topology_path> <options>\n'
   strHelp += 'Options can be, in any order:\n'
   strHelp += '  --mock:   Runs mock experiment, without any calls to Mininet, MiniNDN, NFD, NLSR, ...\n'
   strHelp += '  --sdn:    SDN experiment with Ryu controller\n'
   strHelp += '  --icn:    ICN experiment without specific controller\n'
   strHelp += '  --ip:     IP experiment, no specific controller or cache\n'
   strHelp += '  --ip_sdn: IP with SDN experiment, with Ryu controller and no cache\n'
   print(strHelp)

# ---------------------------------------- Main
def main():

   global g_bIsMockExperiment, g_strNetworkType, g_bMinindnLibsImported

   strMode = 'icn'
   strTopologyPath = ''
   short_options = 'hmt:'
   long_options  = ['help', 'mock', 'sdn', 'icn', 'ip', 'ip_sdn', 'topology=']
   opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
   for opt, arg in opts:
      if opt in ['-h', '--help']:
         showHelp()
         exit(0)
      elif opt in ('-t', '--topology'):
         strTopologyPath = arg
         logging.info('[main] Topology path=%s' % strTopologyPath)
      elif opt in ['-m', '--mock']:
         g_bIsMockExperiment = True
      elif opt == '--sdn':
         strMode = 'sdn'
      elif opt == '--icn':
         strMode = 'icn'
      elif opt == '--ip':
         strMode = 'ip'
      elif opt == '--ip_sdn':
         strMode = 'ip_sdn'

   setNetworkType(strMode)
   # Reset argv arguments for the minindn CLI
   sys.argv = [sys.argv[0]]

   # Check if topology was specified
   if (strTopologyPath == ''):
      logging.error('[main] No topology file specified!')
      showHelp()
      exit(0)

   if (g_strNetworkType == ''):
      logging.error('[main] No network type set')
      showHelp()
      exit(0)

   if(g_bIsMockExperiment):
      runMock(strTopologyPath)
   else:
      if (g_bMinindnLibsImported):
         runExperiment(strTopologyPath)
      else:
         logging.error('[main] Experiment can not run because MiniNDN libraries could not be imported')

if __name__ == '__main__':
   main()
