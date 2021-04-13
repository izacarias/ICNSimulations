import matplotlib
import logging
from datetime import timedelta

from icnexperiment.result_analysis import *
from icnexperiment.dir_config import c_strLogDir

c_strLogFile = c_strLogDir + 'delay_over_time.log'
logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():
   strPath = '/home/andre/results_1204/minindn-ip'
   (hshNodes, lstTransmissions) = readConsumerLogs(strPath)
   logging.info('[main] transmissions=%d' % len(lstTransmissions))
   getSampledAvgs(lstTransmissions, 5)

def getSampledAvgs(lstTransmissions, nSampleSec):
   """
   Returns a type hash containing a tuple with two lists: [0] -> timestamps, [1] -> averages
   """
   # Organize transmissions into lists ordered by timestamps
   hshTypes ={}
   for pTrans in hshTypes:
      if (pTrans.isData()):
         logging.info('data')
         if (pTrans.nDataID not in hshTypes):
            logging.info('[getSamplesAvgs] type=%d' % pTrans.nDataID)
            hshTypes[pTrans.nDataID] = []
         hshTypes[pTrans.nDataID].append(pTrans)

   hshReturn = {}
   for nType in hshTypes:
      logging.info('[getSampledAvgs] Type=%d' % nType)
      hshTypes[nType].sort(key=lambda x: x.dtDate)

      lstTypeTrans = hshTypes[nType]
      nIndex       = 0
      dtStart      = lstTypeTrans[0].dtDate
      while(dtStart <= lstTypeTrans[-1].dtDate):
         logging.info('[getSampledAvgs] Starting period [%s, %s]' % (dtStart.strftime('%H:%M:%S'), (dtStart+timedelta(seconds=nSampleSec)).strftime('%H:%M:%S')))

         lstTimes  = [dtStart]
         lstAvgs   = []
         sDelaySum = 0.0
         nSamples  = 0
         hshReturn[nType] = (lstTimes, lstAvgs)
         # Accumulate sum over nSampleSec period
         while(lstTypeTrans[nIndex].dtDate < (dtStart + timedelta(seconds=nSampleSec))):
            sDelaySum += lstTypeTrans[nIndex].sDelayUs
            nSamples  += 1
            nIndex    += 1

         # Finish average calculation for this sample
         sAvg = sDelaySum/nSamples
         logging.info('[getSampledAvgs] Period end with dtDate=%s; sum=%.2f; samples=%d; avg=%.2f' % (lstTypeTrans[nIndex].dtDate.strftime('%H:%M:%S'), sDelaySum, nSamples, sAvg))
         lstAvgs.append(sAvg)
         # Prepare for next loop
         dtStart += timedelta(seconds=nSampleSec)

   return hshReturn

if (__name__ == '__main__'):
   main()