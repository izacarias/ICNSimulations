"""
This MiniNDN experiment instantiates consumers and producers based on the
packages and their timestamps created and queued by DataManager.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
from data_generation.generics import curDatetimeToFloat
from data_generation.data_manager import DataManager
import sys
import time
import logging
from random import randint
from datetime import datetime, timedelta
from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from mininet.node import Ryu

# ---------------------------------------- Constants
c_strEportCmd        = 'export HOME=/home/osboxes/ && '
c_strAppName         = 'C2Data'
c_strLogFile         = './random_talks.log'
c_strTopologyFile    = '/home/vagrant/icnsimulations/topologies/default-topology.conf'
c_nSleepThresholdMs  = 100
c_sExperimentTimeSec = 60
c_nMissionMinutes    = 5
c_bIsMockExperiment  = False
c_bSDNEnabled        = False

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
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

   def setup(self):
      """
      Setup experiment
      """
      self.log('setup', 'Setting up new experiment')

      # Generate data queue
      lstHostNames = []
      for node in self.lstHosts:
         self.log('setup', 'Node: ' + str(node))
         lstHostNames.append(str(node))
      self.lstDataQueue = self.pDataManager.generateSpreadDataQueue(lstHostNames, c_nMissionMinutes)

      # Get TTLs from data manager
      strTTLValues = self.pDataManager.getTTLValuesParam()
      strPayloadValues = self.pDataManager.getPayloadValuesParam()

      # Instantiate all producers
      for pHost in self.lstHosts:
         self.instantiateProducer(pHost, strTTLValues, strPayloadValues)

      # Log resulting data queue
      for nIndex, node in enumerate(self.lstDataQueue):
         self.log('setup', 'Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))

   def run(self):
      """
      Experiment routine
      """
      self.log('run', 'Running')

      # Internal parameters
      nHosts             = len(self.lstHosts)
      dtInitialTime      = datetime.now()
      dtCurTime          = None
      dtDelta            = timedelta()
      nDataIndex         = 0
      sElapsedTimeMs     = 0
      while (((sElapsedTimeMs/1000) < c_sExperimentTimeSec) and (nDataIndex < len(self.lstDataQueue))):
         # Send data until the end of the experiment time
         # Sweep queue and send data according to the elapsed time
         dtCurTime       = datetime.now()
         dtDelta         = dtCurTime - dtInitialTime
         sElapsedTimeMs  = dtDelta.microseconds/1000 + dtDelta.seconds*1000
         pDataBuff       = self.lstDataQueue[nDataIndex]
         self.log('run', 'new iteration with sElapsedTimeMs=%s; dtDelta=%s' % (sElapsedTimeMs, str(dtDelta)))

         if (pDataBuff[0] <= sElapsedTimeMs):
            # Send data
            self.log('run', 'about to send data nDataIndex=%s; pDataBuff[0]=%s; sElapsedTimeMs=%s' %
               (nDataIndex, pDataBuff[0], sElapsedTimeMs))
            self.instantiateConsumer(pDataBuff[1])
            nDataIndex += 1
         else:
            # Wait before sending next data
            self.log('run', 'waiting to send next data package nDataIndex=%s; pDataBuff[0]=%s; sElapsedTimeMs=%s' %
               (nDataIndex, pDataBuff[0], sElapsedTimeMs))

         # Wait until next data is ready, if past threshold
         if (nDataIndex < len(self.lstDataQueue)):
            nNextStopMs = self.lstDataQueue[nDataIndex][0] - sElapsedTimeMs
            if (nNextStopMs > c_nSleepThresholdMs):
               self.log('run', 'sleeping until next data nNextStopMs=%s; c_nSleepThresholdMs=%s' % (nNextStopMs, c_nSleepThresholdMs))
               time.sleep(nNextStopMs/1000.0)

      # Close log file
      self.log('run', 'experiment done in %s seconds log written to %s' % (sElapsedTimeMs/1000, c_strLogFile))

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
         self.log('instantiateConsumer', 'ConsumerCmd: ' + strCmdConsumer)
      else:
         raise Exception('[instantiateConsumer] ERROR, invalid origin host in data package=%s' % pDataPackage)

   def instantiateProducer(self, pHost, strTTLValues, strPayloadValues):
      """
      Issues MiniNDN commands to instantiate a producer
      """
      strFilter       = self.getFilterByHostname(str(pHost))
      strCmdAdvertise = 'nlsrc advertise %s' % strFilter
      strCmdProducer  = 'producer %s %s %s &' % (strFilter, strTTLValues, strPayloadValues)
      pHost.cmd(strCmdAdvertise)
      pHost.cmd(strCmdProducer)
      self.log('instantiateProducer', 'instantiating new producer ' + str(pHost) + ' ' + strFilter + ' &')
      self.log('instantiateProducer', 'AdvertiseCmd: ' + strCmdAdvertise)
      self.log('instantiateProducer', 'ProducerCmd: ' + strCmdProducer)

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

   def log(self, strFunction, strContent):
      """
      Logs a line in the Andre standard format
      """
      strLine = '[RandomTalks.' + strFunction + '] ' + strContent
      logging.info(strLine)

# ---------------------------------------- MockHost
class MockHost():

   def __init__(self, strName):
      # Shit
      self.strName = strName

   def __repr__(self):
      return self.strName

   def cmd(self, strLine):
      return 0


def runMock():
   """
   Runs mock experiment. No cummunication with Mininet or MiniNDN
   """
   lstHosts = [MockHost('d1'), MockHost('s1'), MockHost('h1'), MockHost('v1'), MockHost('h2'), MockHost('s2'), MockHost('d2')]
   Experiment = RandomTalks(lstHosts)
   Experiment.setup()
   Experiment.run()

def runExperiment():
   """
   Runs experiment
   """
   setLogLevel('info')
   Minindn.cleanUp()
   Minindn.verifyDependencies()

   if (c_bSDNEnabled):
      ndn = Minindn(topoFile=c_strTopologyFile, controller=Ryu)
   else:
      ndn = Minindn(topoFile=c_strTopologyFile)
   ndn.start()

   info('Starting NFD on nodes\n')
   nfds = AppManager(ndn, ndn.net.hosts, Nfd)
   nHosts = len(ndn.net.hosts)

   # lstHosts = ndn.net.hosts[0:min(2,nHosts)]
   # nfds1 = AppManager(ndn, lstHosts, Nfd, csSize=0)
   # for x in lstHosts:
   #    print('Cache 0: %s' % str(x))

   # lstHosts = ndn.net.hosts[2:min(4,nHosts)]
   # nfds2 = AppManager(ndn, lstHosts, Nfd, csSize=100)
   # for x in lstHosts:
   #    print('Cache 100: %s' % str(x))

   # lstHosts = ndn.net.hosts[4:min(6,nHosts)]
   # nfds3 = AppManager(ndn, lstHosts, Nfd, csSize=1000)
   # for x in lstHosts:
   #    print('Cache 1000: %s' % str(x))

   # lstHosts = ndn.net.hosts[6:nHosts]
   # nfds4 = AppManager(ndn, lstHosts, Nfd, csSize=10000)
   # for x in lstHosts:
   #    print('Cache 10000: %s' % str(x))
      

   info('Starting NLSR on nodes\n')
   nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

   #############################################################
   # Wait for NLSR initialization, 30 seconds to be on the safe side
   time.sleep(30)

   # Set up experiment
   Experiment = RandomTalks(ndn.net.hosts)
   Experiment.setup()
   Experiment.run()

   MiniNDNCLI(ndn.net)
   ndn.stop()

# ---------------------------------------- Main
if __name__ == '__main__':

   if(c_bIsMockExperiment):
      runMock()
   else:
      runExperiment()
