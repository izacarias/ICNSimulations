#!/usr/bin/python
"""
This MiniNDN experiment instantiates consumers and producers based on the
packages and their timestamps created and queued by DataManager.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import sys
import time
import logging
from random   import randint
from datetime import datetime, timedelta

from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from mininet.node import Ryu

from icnexperiment.data_generation import DataManager, curDatetimeToFloat, readHostNamesFromTopoFile
from icnexperiment.log_dir import c_strLogDir

# ---------------------------------------- Constants  
c_strAppName         = 'C2Data'
c_strLogFile         = c_strLogDir + 'experiment_send.log'
c_strTopologyFile    = '/home/vagrant/icnsimulations/topologies/default-topology.conf'

c_bIsMockExperiment  = True
c_nSleepThresholdMs  = 100
c_sExperimentTimeSec = 10*60

c_bSDNEnabled       = True
c_nCacheSizeDefault = 65536
c_nHumanCacheSize   = c_nCacheSizeDefault 
c_nDroneCacheSize   = c_nCacheSizeDefault
c_nSensorCacheSize  = c_nCacheSizeDefault 
c_nVehicleCacheSize = c_nCacheSizeDefault

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# ---------------------------------------- RandomTalks
class RandomTalks():

   def __init__(self, lstHosts):
      """
      Constructor. Meh
      """
      self.logFile         = None
      self.pDataManager    = DataManager()
      self.lstHosts        = lstHosts

   def setup(self, strTopoPath):
      """
      Setup experiment
      """
      logging.info('[RandomTalks.setup] Setting up new experiment')

      # Load data queue
      self.lstDataQueue = DataManager.loadDataQueueFromFile(strTopoPath)

      # Get TTLs from data manager
      strTTLValues = self.pDataManager.getTTLValuesParam()
      strPayloadValues = self.pDataManager.getPayloadValuesParam()

      # Instantiate all producers
      for pHost in self.lstHosts:
         self.instantiateProducer(pHost, strTTLValues, strPayloadValues)

      # Log resulting data queue
      for nIndex, node in enumerate(self.lstDataQueue):
         logging.info('[RandomTalks.setup] Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))

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
         strCmdConsumer = 'consumer %s %s %f' % (strInterest, str(pConsumer), sTimestamp)
         pConsumer.cmd(strCmdConsumer)
         logging.debug('[RandomTalks.instantiateConsumer] ConsumerCmd: ' + strCmdConsumer)
      else:
         raise Exception('[RandomTalks.instantiateConsumer] ERROR, invalid origin host in data package=%s' % pDataPackage)

   def instantiateProducer(self, pHost, strTTLValues, strPayloadValues):
      """
      Issues MiniNDN commands to instantiate a producer
      """
      strFilter       = self.getFilterByHostname(str(pHost))
      strCmdAdvertise = 'nlsrc advertise %s' % strFilter
      strCmdProducer  = 'producer %s %s %s &' % (strFilter, strTTLValues, strPayloadValues)
      pHost.cmd(strCmdAdvertise)
      pHost.cmd(strCmdProducer)
      logging.debug('[RandomTalks.instantiateProducer] Instantiating new producer ' + str(pHost) + ' ' + strFilter + ' &')
      logging.debug('[RandomTalks.instantiateProducer] AdvertiseCmd: ' + strCmdAdvertise)
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
      return '/' + c_strAppName + '/' + strName + '/'

# ---------------------------------------- MockHost
class MockHost():

   def __init__(self, strName):
      # Shit
      self.strName = strName

   def __repr__(self):
      return self.strName

   def cmd(self, strLine):
      return 0


def runMock(strTopoPath):
   """
   Runs mock experiment. No cummunication with Mininet or MiniNDN
   """
   lstHostNames = readHostNamesFromTopoFile(strTopoPath)
   lstHosts = [MockHost(strName) for strName in lstHostNames]
   Experiment = RandomTalks(lstHosts)
   Experiment.setup(strTopoPath)
   Experiment.run()

def runExperiment(strTopoPath):
   """
   Runs experiment
   """
   setLogLevel('info')
   Minindn.cleanUp()
   Minindn.verifyDependencies()

   ######################################################
   # Start MiniNDN and set controller, if any
   if (c_bSDNEnabled):
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

   nfdsHuman = AppManager(ndn, lstHumanHosts, Nfd, csSize=c_nHumanCacheSize)
   info('[runExperiment] Cache set for humans=%d, size=%d\n' % (len(lstHumanHosts), c_nHumanCacheSize))
   nfdsDrone = AppManager(ndn, lstDroneHosts, Nfd, csSize=c_nDroneCacheSize)
   info('[runExperiment] Cache set for drones=%d, size=%d\n' % (len(lstDroneHosts), c_nDroneCacheSize))
   nfdsSensor = AppManager(ndn, lstSensorHosts, Nfd, csSize=c_nSensorCacheSize)
   info('[runExperiment] Cache set for sensors=%d, size=%d\n' % (len(lstSensorHosts), c_nSensorCacheSize))
   nfdsVehicle = AppManager(ndn, lstVehicleHosts, Nfd, csSize=c_nVehicleCacheSize)
   info('[runExperiment] Cache set for vehicles=%d, size=%d\n' % (len(lstVehicleHosts), c_nVehicleCacheSize))

   ##########################################################
   # Initialize NFD
   info('Starting NLSR on nodes\n')
   nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

   ##########################################################
   # Wait for NLSR initialization, at least 30 seconds to be on the safe side
   time.sleep(40)

   ##########################################################
   # Set up and run experiment
   Experiment = RandomTalks(ndn.net.hosts)
   Experiment.setup(strTopoPath)
   Experiment.run()

   MiniNDNCLI(ndn.net)
   ndn.stop()

# ---------------------------------------- Main
def main():

   # Read input param for topology
   if (len(sys.argv) == 1):
      logging.error('[setup] no topology file specified. To use default, use \'default\' as the first parameter')
      exit()
   elif (sys.argv[1] == 'default'):
      strTopologyPath = c_strTopologyFile
   else:
      strTopologyPath = sys.argv[1]

   if(c_bIsMockExperiment):
      runMock(strTopologyPath)
   else:
      runExperiment(strTopologyPath)

if __name__ == '__main__':
   main()
