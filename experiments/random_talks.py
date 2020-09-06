import sys
import time
import logging
from DataManager import *
from random      import randint
from datetime    import datetime, timedelta
from ndn.experiments.experiment import Experiment

# ---------------------------------------- Constants
c_strEportCmd       = 'export HOME=/home/osboxes/ && '
c_strAppName        = 'C2Data'
c_strLogFile        = '/home/osboxes/random_talks.log'
c_nSleepThresholdMs = 100
c_bIsMockExperiment = False

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# ---------------------------------------- RandomTalks
class RandomTalks(Experiment):

   def __init__(self, args):
      """
      Constructor. Meh
      """
      self.logFile         = None
      self.DataManager     = DataManager()
      self.nMissionMinutes = 1
      self.lstHosts        = []
      if (not c_bIsMockExperiment):
         Experiment.__init__(self, args)

   def setup(self):
      """
      Setup experiment
      """
      if (c_bIsMockExperiment):
         self.lstHosts = ['d1', 's1', 'h1', 'v1', 'h2', 's2', 'd2']
      else:
         self.lstHosts = self.net.hosts

      self.log('setup', 'Setting up new experiment')

      # Generate data queue
      lstHostNames = []
      for node in self.lstHosts:
         self.log('setup', 'Node: ' + str(node))
         lstHostNames.append(str(node))
      self.lstDataQueue = self.DataManager.generateDataQueue(lstHostNames, self.nMissionMinutes)

      # Instantiate all producers
      for pHost in self.lstHosts:
         strFilter = self.getFilterByHostname(str(pHost))
         pHost.cmd('producer ' + strFilter + ' &')
         self.log('setup', 'instantiating new producer ' + str(pHost) + ' ' + strFilter + ' &')

      # Log resulting data queue
      for nIndex, node in enumerate(self.lstDataQueue):
         self.log('setup', 'Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))      

   def run(self):
      """
      Experiment routine
      """
      self.log('run', 'Running')

      # User parameters
      sExperimentTimeSec = 30

      # Internal parameters
      nHosts             = len(self.lstHosts)
      dtInitialTime      = datetime.now()
      dtCurTime          = None
      dtDelta            = timedelta()
      nDataIndex         = 0
      sElapsedTimeMs     = 0
      while (((sElapsedTimeMs/1000) < sExperimentTimeSec) and (nDataIndex < len(self.lstDataQueue))):
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
            self.send(pDataBuff[1])
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
               time.sleep(nNextStopMs/1000)

      # Close log file
      self.log('run', 'experiment done in %s seconds log written to %s' % (sElapsedTimeMs/1000, c_strLogFile))

   def send(self, pDataPackage):
      """
      Issues MiniNDN commands for sender and receiver of a data package
      @param pDataPackage: DataPackage
      """
      # Find consumer associated to the package
      nConsumer = self.findHostByName(pDataPackage.strDest)

      if(nConsumer >= 0):
          # Valid consumer and producer
         pConsumer = self.lstHosts[nConsumer]
         strInterest = pDataPackage.getInterest()
         self.log('send', 'instantiating new consumer ' + str(pConsumer) + ' ' + strInterest + ' &')
         pConsumer.cmd('consumer %s %s &' % (strInterest, str(pConsumer)))
      else:
         raise Exception('[send] ERROR, invalid origin host in data package=%s' % pDataPackage)

   def findHostByName(self, strName):
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


if (c_bIsMockExperiment):
   talks = RandomTalks('')
   talks.setup()
   talks.run()
else:
   Experiment.register("random-talks", RandomTalks)

