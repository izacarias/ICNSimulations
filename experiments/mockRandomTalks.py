import sys
import time
import logging
from DataManager import *
from random      import randint
from datetime    import datetime, timedelta
# from ndn.experiments.experiment import Experiment

c_strEportCmd = 'export HOME=/home/osboxes/ && '
c_strAppName  = 'C2Data'
# c_strLogFile  = '/home/osboxes/random_talks.log'
c_strLogFile  = './random_talks.log'
c_nSleepThresholdMs = 100
logging.basicConfig(filename="experiment.log", format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


class RandomTalks():

   def __init__(self):
      """
      Constructor. Meh
      """
      self.logFile         = None
      self.lstProducers    = []
      self.DataManager     = DataManager()
      self.nMissionMinutes = 1
      self.lstHosts        = []

   def setup(self):
      """
      Setup experiment
      """
      self.lstHosts = ['d1', 's1', 'h1', 'v1', 'h2', 's2', 'd2']

      self.log('setup', 'Setting up new experiment')

      lstHostNames = []
      for node in self.lstHosts:
         self.log('setup', 'Node: ' + str(node))
         lstHostNames.append(str(node))

      self.lstDataQueue = self.DataManager.generateDataQueue(lstHostNames, self.nMissionMinutes)

      for nIndex, node in enumerate(self.lstDataQueue):
         self.log('setup', 'Node[' + str(nIndex) + ']: ' + str(node[0]) + ', ' + str(node[1]))

   def run(self):
      """
      Experiment routine
      """
      self.log('run', 'Running')

      # Internal parameters
      nHosts             = len(self.lstHosts)
      lstProducers       = []
      dtInitialTime      = datetime.now()
      dtCurTime          = None
      dtDelta            = timedelta()
      sExperimentTimeSec = 100
      nDataIndex         = 0
      sElapsedTimeMs     = 0
      while (((sElapsedTimeMs/1000) < sExperimentTimeSec) and (nDataIndex < len(self.lstDataQueue))):
         # Send data until the end of the experiment time
         # Sweep queue and send data according to the elapsed time
         dtCurTime       = datetime.now()
         dtDelta         = dtCurTime - dtInitialTime
         sElapsedTimeMs  = dtDelta.microseconds/1000 + dtDelta.seconds*1000
         self.log('run', 'new iteration with sElapsedTimeMs=%s; dtDelta=%s' % (sElapsedTimeMs, str(dtDelta)))

         # if (dtDelta.seconds > 0):
         #    raise Exception('RandomTalks.run: Error, time delta > 1s')

         pDataBuff = self.lstDataQueue[nDataIndex]

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
      if (self.logFile):
         self.logFile.close()

   def send(self, pDataPackage):
      """
      Issues MiniNDN commands for sender and receiver of a data package
      @param pDataPackage: DataPackage
      """
      # Find agents associated to the package
      nProducer = self.findHostByName(pDataPackage.strOrig)
      nConsumer = self.findHostByName(pDataPackage.strDest)

      if((nProducer >= 0) and (nConsumer >= 0)):
          # Valid consumer and producer
         pProducer = self.lstHosts[nProducer]
         pConsumer = self.lstHosts[nConsumer]

         if(nProducer not in self.lstProducers):
            # Producer has not yet been instantiated
            strFilter = self.getFilterByHostname(pDataPackage.strOrig)
            self.log('send', 'instantiating new producer ' + str(pProducer) + ' ' + strFilter + ' &')
            self.log('send', 'cmd: producer ' + strFilter + ' &')
            # pProducer.cmd('producer ' + strFilter + ' &')
            self.lstProducers.append(nProducer)

         strInterest = pDataPackage.getInterest()
         self.log('send', 'instantiating new consumer ' + str(pConsumer) + ' ' + strInterest + ' &')
         self.log('send', 'cmd: consumer %s &' % (strInterest))
         #  pConsumer.cmd('consumer %s &' % (strInterest))
         self.log('send', 'Sending %s' % pDataPackage)
      else:
         raise Exception('[send] ERROR, invalid origin or destination hosts in data package=%s' % pDataPackage)

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
      if (not self.logFile):
         self.logFile = open(c_strLogFile, 'a+')
         self.logFile.write('New run -----------------------------------------\n')

      strLine = '[RandomTalks.' + strFunction + '] ' + strContent

      # self.logFile.write(strLine + '\n')
      logging.info(strLine)
      # print(strLine)

# Experiment.register("random-talks", RandomTalks)

# ------------------------------------------------------------------------

talks = RandomTalks()
talks.setup()
talks.run()

print('Done')


# self.net.hosts -> self.lstHosts