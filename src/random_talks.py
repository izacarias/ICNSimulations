#!/usr/bin/python
"""
This MiniNDN experiment instantiates consumers and producers based on the
packages and their timestamps created and queued by DataManager.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import sys
import os
import time
import logging
import getopt
import psutil
import subprocess
from random   import randint
from datetime import datetime, timedelta

from icnexperiment.data_generation import DataManager, curDatetimeToFloat

# ---------------------------------------- Constants
c_sConsumerCooldownSec    = 0.0
c_nSleepThresholdMs       = 100
c_sExperimentTimeSec      = 100

g_bIsMockExperiment       = False

g_dtLastProducerCheck     = None
g_nProducerCheckPeriodSec = 5

# ---------------------------------------- RandomTalks
class RandomTalks():

   def __init__(self, lstHosts, lstDataQueue):
      """
      Constructor. Meh
      """
      self.logFile          = None
      self.pDataManager     = DataManager()
      self.lstHosts         = lstHosts
      self.strTTLValues     = 'None'
      self.strPayloadValues = 'None'
      self.lstDataQueue     = lstDataQueue
      self.nBytesConsumed   = 0
      self.hshConsumers     = {}
      self.strPayloadPath   = '/home/vagrant/mock_data'
      self.lstRunningPutChunks = []
      self.hshPutchunksProcs = {}

   def setup(self):
      """
      Setup experiment
      """
      logging.info('[RandomTalks.setup] Setting up new experiment')
      self.nBytesConsumed = 0
      
      self.hshConsumers = {}
      for pHost in self.lstHosts:
         self.hshConsumers[str(pHost)] = datetime(1,1,1,0,0)

      # Get TTLs from data manager
      self.strTTLValues     = self.pDataManager.getTTLValuesParam()
      self.strPayloadValues = self.pDataManager.getPayloadValuesParam()

      # Create payload mock files
      DataManager.createPayloadFiles(self.lstDataQueue, self.strPayloadPath)

      # Get average payload size from DataManager. This will be used to set cache sizes in the future
      sPayloadAvg = self.pDataManager.avgPayloadSize()
      logging.info('[RandomTalks.setup] avgPayloadSize=%.3f' % sPayloadAvg)

      # Instantiate all producers
      # self.checkRunningProducers()

      # Log the current configuration for data_manager
      logging.debug('[RandomTalks.setup] Current data type configuration: \n%s' % self.pDataManager.info())
      logging.debug('[RandomTalks.setup] Note that this could be outdated since the data queue configuration is set when it is created!')

   def run(self):
      """
      Experiment routine. Returns tuple (dtBegin, dtEnd).
      """
      logging.info('[RandomTalks.run] Begin, maxExperimentTimeSec=%f' % c_sExperimentTimeSec)

      # Internal parameters
      dtBegin        = datetime.now()
      dtNow          = None
      dtDelta        = timedelta()
      nDataIndex     = 0
      sElapsedTimeMs = 0
      nIteration     = 0
      sTimeDiffSum   = 0
      sTimeDiffAvg   = 0
      while (((sElapsedTimeMs/1000) < c_sExperimentTimeSec) and (nDataIndex < len(self.lstDataQueue))):
         # Send data until the end of the experiment time
         # Sweep queue and send data according to the elapsed time
         dtNow      = datetime.now()
         dtDelta        = dtNow - dtBegin
         sElapsedTimeMs = dtDelta.microseconds/1000 + dtDelta.seconds*1000
         nIteration    += 1
         logging.debug('[RandomTalks.run] New iteration with sElapsedTimeMs=%s; dtDelta=%s' % (sElapsedTimeMs, str(dtDelta)))

         while (nDataIndex < len(self.lstDataQueue)) and (self.lstDataQueue[nDataIndex][0] <= sElapsedTimeMs):
            # Send data
            pDataBuff = self.lstDataQueue[nDataIndex]
            
            sTimeDiffMs   = sElapsedTimeMs - pDataBuff[0]
            sTimeDiffSum += sTimeDiffMs
            sTimeDiffAvg  = float(sTimeDiffSum)/(nDataIndex+1)
	    
            if (sTimeDiffMs > 5):
               logging.info('[RandomTalks.run] About to send data nDataIndex=%d/%d; elapsedSec=%s; timeDiffMs=%s, timeDiffAvg=%.2f, MBytesConsumed=%.3f' % (nDataIndex, len(self.lstDataQueue)-1, sElapsedTimeMs/1000.0, sTimeDiffMs, sTimeDiffAvg, self.nBytesConsumed/(1024.0*1024.0)))

            # Instantiate consumer and producer host associated in the data package
            pDataPackage = pDataBuff[1]
            pProducer = self.findHostByName(pDataPackage.strOrig)
            pConsumer = self.findHostByName(pDataPackage.strDest)

            # In some setups, producer hosts might be killed by the OS for an unknown reason
            # This makes sure producers are running correctly during the simulation
            # As of 03/2021 this is not happening anymore. Possibly because of the call to getPopen(pHost, strCmdConsumer) instead of pHost.cmd (??)
            # self.checkRunningProducers()
            if(not self.isProducerRunning(pDataPackage)):
               self.instantiateProducer(pProducer, pDataPackage)
               time.sleep(0.2)

            self.instantiateConsumer(pConsumer, pDataPackage)
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
      # self.killAllProducers()
      logging.info('[RandomTalks.run] Experiment done in %s seconds' % (sElapsedTimeMs/1000))
      return (dtBegin, datetime.now())
 
   def checkRunningProducers(self):
      """
      Checks for all producer processes periodicaly. The period is set by g_nProducerCheckPeriodSec.
      """
      global g_nProducerCheckPeriodSec, g_dtLastProducerCheck

      if (g_dtLastProducerCheck is None) or (g_dtLastProducerCheck + timedelta(seconds=g_nProducerCheckPeriodSec) <= datetime.now()):

         logging.info('[RandomTalks.checkRunningProducers] Started check')

         lstRunningProducers = []
         for proc in psutil.process_iter():
            try:
               # Exceptions can happen here as processes are spawned and killed concurrently
               if (proc.name() == 'producer'):
                  # Second parameter should be the interest filter
                  strHost = RandomTalks.getHostnameFromFilter(proc.cmdline()[1])
                  lstRunningProducers.append(strHost)
            except:
               pass
         
         logging.info('[RandomTalks.checkRunningProducers] Found %d running producer programs, missing=%d' % (len(lstRunningProducers), len(self.lstHosts)-len(lstRunningProducers)))

         if (g_dtLastProducerCheck is None) and (len(lstRunningProducers) > 0):
            logging.critical('[RandomTalks.checkRunningProducers] first producer check, found %d producers already running' % len(lstRunningProducers))
      
         for pHost in self.lstHosts:
            if (str(pHost) not in lstRunningProducers):
               logging.info('[RandomTalks.checkRunningProducers] instantiating missing producer=%s' % str(pHost))
               self.instantiateProducer(pHost)
      
         # Update last check time
         g_dtLastProducerCheck = datetime.now()

   def instantiateProducer(self, pHost, pDataPackage):
      """
      Issues MiniNDN commands to instantiate a producer
      """
      global g_bIsMockExperiment
      if (pHost):
         nTTL = self.pDataManager.getTTLForDataType(pDataPackage.nType)
         strFilter = RandomTalks.getChunksFilter(pDataPackage.strOrig, pDataPackage.nType, pDataPackage.nID)
         strFilePath = DataManager.nameForPayloadFile(pDataPackage.nPayloadSize, self.strPayloadPath)
         strCmd = 'ndnputchunks %s -f %d < %s' % (strFilter, nTTL, strFilePath)
         if (not g_bIsMockExperiment):
            # getPopen(pHost, strCmd, shell=True)
            proc = pHost.popen(strCmd, shell=True)
         
         if (pHost.name not in self.hshPutchunksProcs):
            self.hshPutchunksProcs[pHost.name] = []
         
         self.addProducerProcess(pHost.name, proc, strFilter)
         logging.info('[RandomTalks.instantiateProducer] ProducerCmd: ' + strCmd)
      else:
         logging.critical('[RandomTalks.instantiateProducer] Producer is nil!')
      
   def instantiateConsumer(self, pHost, pDataPackage):
      """
      Issues MiniNDN commands to set up a consumer for a data package
      """
      global g_bIsMockExperiment
      if (pHost):
         # Consumer program usage: consumer <interest> <hostName> <payload> <timestamp>
         sSecSinceLast = (datetime.now() - self.hshConsumers[str(pHost)]).total_seconds()
         if (sSecSinceLast < c_sConsumerCooldownSec):
            logging.info('[RandomTalks.instantiateConsumer] Will wait seconds=%.2f' % (c_sConsumerCooldownSec - sSecSinceLast))
            time.sleep(c_sConsumerCooldownSec - sSecSinceLast)

         strInterest = RandomTalks.getChunksFilter(pDataPackage.strOrig, pDataPackage.nType, pDataPackage.nID)
         strCmd = 'ndncatchunks %s' % strInterest
         if (not g_bIsMockExperiment):
            # getPopen(pHost, strCmd, shell=True)
            proc = pHost.popen(strCmd, shell=True)

         self.nBytesConsumed += pDataPackage.nPayloadSize        
         logging.info('[RandomTalks.instantiateConsumer] %s ConsumerCmd: %s' % (pHost.name, strCmd))
      else:
         logging.critical('[RandomTalks.instantiateConsumer] Host is nil! host=%s' % str(pHost))

   def addProducerProcess(self, strHost, newProc, strInterest):
      nMaxProcsPerHost = 30
      if (strHost not in self.hshPutchunksProcs):
         self.hshPutchunksProcs[strHost] = []
      self.hshPutchunksProcs[strHost].append([newProc, strInterest])

      if (len(self.hshPutchunksProcs[strHost]) > nMaxProcsPerHost):
         # Kill and remove the oldest process
         [oldProc, strOldInt] = self.hshPutchunksProcs[strHost].pop(0)
         oldProc.kill()
         logging.info('[RandomTalks.addProducerProcess] Remove old process from host=%s for interest=%s' % (strHost, strOldInt))
      return

   def isProducerRunning(self, pDataPackage):
      bIsRunning = False
      strFilter  = RandomTalks.getChunksFilter(pDataPackage.strOrig, pDataPackage.nType, pDataPackage.nID)
      if (pDataPackage.strOrig in self.hshPutchunksProcs):
         for [proc, strRunningFilter] in self.hshPutchunksProcs[pDataPackage.strOrig]:
            if (strRunningFilter == strFilter):
               bIsRunning = True
               break
      return bIsRunning

   def killAllProducers(self):
      for strHost in self.hshPutchunksProcs:
         for [proc, strInterest] in self.hshPutchunksProcs[strHost]:
            proc.kill()

   def findHostByName(self, strHostName):
      """
      Returns a host found in the host list.
      """
      pResultHost = None
      for pHost in self.lstHosts:
         if (str(pHost) == strHostName):
            pResultHost = pHost
      return pResultHost  

   @staticmethod
   def getFilterByHostname(strName):
      """
      Creates interest filter base on the producer`s name
      """
      # return '/' + c_strAppName + '/' + strName + '/'
      return '/%s/' % (strName)
      # return '/ndn/%s-site/%s/' % (strName, strName)

   @staticmethod
   def getHostnameFromFilter(strInterestFilter):
      """
      Returns a hostname read from an interest filter
      """
      return strInterestFilter.split('/')[-2]

   @staticmethod
   def getChunksFilter(strProd, nType, nId):
      return '%sType%dId%d/' % (RandomTalks.getFilterByHostname(strProd), nType, nId)
