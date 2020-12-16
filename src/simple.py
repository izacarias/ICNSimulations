"""
This is a test script which instantiates consumers and producers in
their most basic form. The idea is to test the simplest components used
in a MiniNDN testl.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import sys
import time
import logging
from src.data_generation.data_manager import DataManager
from random       import randint
from datetime     import datetime, timedelta
from mininet.log  import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

# ---------------------------------------- Constants
c_strAppName         = 'Simple'
c_strLogFile         = './random_talks.log'
c_nSleepThresholdMs  = 100
c_bIsMockExperiment  = True

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# ---------------------------------------- RandomTalks
class SimpleTalks():

   def __init__(self, lstHosts):
      """
      Constructor. Meh
      """
      self.logFile         = None
      self.pDataManager    = DataManager()
      self.nMissionMinutes = 1
      self.lstHosts        = lstHosts

   def setup(self):
      """
      Setup experiment
      """
      self.log('setup', 'Setting up new experiment')

      ##################################################
      # Instantiate all producers
      strTTLValues = '1'
      for pHost in self.lstHosts:
         self.instantiateProducer(pHost, strTTLValues)

   def run(self):
      """
      Experiment routine
      """
      self.log('run', 'Running')

      # Instantiates consumers
      pProducer = self.lstHosts[0];
      for pHost in self.lstHosts:
         # Instantiatiate all nodes as consumers
         strInterest    = self.getFilterByHostname(str(pProducer))
         strCmdConsumer = 'consumer %s %s' % (strInterest, str(pHost))
         pHost.cmd(strCmdConsumer)
         self.log('run', 'ConsumerCmd: \'%s\'' % strCmdConsumer)

      # Close log file
      self.log('run', 'experiment done, log written to %s' % c_strLogFile)

   def instantiateProducer(self, pHost, strTTLValues):
      """
      Issues MiniNDN commands to instantiate a producer
      """
      strFilter       = self.getFilterByHostname(str(pHost))
      strCmdAdvertise = 'nlsrc advertise %s' % strFilter
      strCmdProducer  = 'producer %s %s &' % (strFilter, strTTLValues)

      pHost.cmd(strCmdAdvertise)
      pHost.cmd(strCmdProducer)
      self.log('instantiateProducer', 'AdvertiseCmd: ' + strCmdAdvertise)
      self.log('instantiateProducer', 'ProducerCmd: ' + strCmdProducer)

   def getFilterByHostname(self, strName):
      """
      Creates interest filter base on the producer`s name
      """
      return '/' + c_strAppName + '/' + strName + '/'

   def log(self, strFunction, strContent):
      """
      Logs a line in the Andre standard format
      """
      strLine = '[SimpleTalks.' + strFunction + '] ' + strContent
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
   # lstHosts = [MockHost('d1'), MockHost('s1'), MockHost('h1'), MockHost('v1'), MockHost('h2'), MockHost('s2'), MockHost('d2')]
   lstHosts = [MockHost('a'), MockHost('b'), MockHost('c'), MockHost('d')]
   Experiment = SimpleTalks(lstHosts)
   Experiment.setup()
   Experiment.run()

def runExperiment():
   """
   Runs experiment
   """
   setLogLevel('info')
   Minindn.cleanUp()
   Minindn.verifyDependencies()
   ndn = Minindn()
   ndn.start()

   info('Starting NFD on nodes\n')
   nfds = AppManager(ndn, ndn.net.hosts, Nfd)
   info('Starting NLSR on nodes\n')
   nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

   # Set up experiment
   Experiment = SimpleTalks(ndn.net.hosts)
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
