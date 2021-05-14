#!/bin/python

import os
import re
from os.path import basename, dirname

class Experiment(object):
   def __init__(self, strIteration, strMode, strTopo, strItername):
      self.strIteration = strIteration
      self.strItername = strItername
      self.strMode = strMode
      self.strTopo = strTopo
      self.nTotalInterests = 0
      self.nConsumerInterests = 0

   def toString(self):
      return '/%s/%s/%s/%s/total=%d, consumer=%d' % (self.strIteration, self.strItername, self.strMode, self.strTopo, self.nTotalInterests, self.nConsumerInterests)

class ExperimentHost(object):
   def __init__(self, strName):
      self.strName = strName
      self.lstOwnInterests = list()
      self.lstInterests = list()
      self.nOwnInt = 0
      self.nOutgoingInt = 0

def readDataFile(strPath):

   dataFile = open(strPath)
   hshData = {}
   lstLines = dataFile.readlines()
   for strLine in lstLines:
      nConsPos = strLine.find(';Cons=') + len(';Cons=')
      nProdPos = strLine.find('Prod=') + len('Prod=')
      nTypePos = strLine.find('Type=') + len('Type=')
      nPayloadPos = strLine.find(';Payload') + len(';Payload')
      nIdPos = strLine.find(';Id=') + len(';Id=')

      strCons = strLine[nConsPos:].strip()
      strProd = strLine[nProdPos:nConsPos]
      nType = strLine[nTypePos:nIdPos]
      nId = strLine[nIdPos:nPayloadPos]

      if (strCons not in hshData):
         hshData[strCons] = []
      hshData[strCons].append('interest=/%s/Type%dId%d/' % (strProd, nType, nId))

   dataFile.close()
   return hshData

def readNfdLog(strNfdPath):

   try:
      inFile = open(strNfdPath)
   except:
      return (0,0)

   nIncomingInt = 0
   lstInterestFaces = list()
   lstOwnFaces = list()
   if (inFile):
      # print('Host=%s' % basename(dirname(strNfdPath)))
      for strLine in inFile:
         pMatch = re.match(r'.*onIncomingInterest in=\(([0-9]+),[0-9]+\) interest=(\/[vhds].+)', strLine)
         if (pMatch):
            nFaceId = int(pMatch.group(1))
            lstInterestFaces.append(nFaceId)
            nIncomingInt += 1
            # print('face=%d; interest=%s' % (nFaceId, pMatch.group(2)))

         else:
            pMatch = re.match(r'.*Added face id=([0-9]+).+local=unix:\/\/', strLine)
            if (pMatch):
               nFaceId = int(pMatch.group(1))
               lstOwnFaces.append(nFaceId)
               # print('ownFace=%d' % nFaceId)

   inFile.close()
   nTotalInterests = len(lstInterestFaces)

   for nOwnFace in lstOwnFaces:
      while (nOwnFace in lstInterestFaces):
         lstInterestFaces.remove(nOwnFace)

   nOwnInterests = nTotalInterests - len(lstInterestFaces)
   return (nTotalInterests, nOwnInterests)

strBaseDir = '/home/vagrant/nfdlogs/'
lstExperiments = list()
for strIteration in os.listdir(strBaseDir):
   for strMode in os.listdir(strBaseDir + strIteration):
      for strTopo in os.listdir(strBaseDir + strIteration + '/' + strMode):
         for strItername in os.listdir(strBaseDir + strIteration + '/' + strMode + '/' + strTopo):
            newExp = Experiment(strIteration, strMode, strTopo, strItername)
            lstExperiments.append(newExp)
            for strHost in os.listdir(strBaseDir + strIteration + '/' + strMode + '/' + strTopo + '/' + strItername):
               strNfdPath = strBaseDir + strIteration + '/' + strMode + '/' + strTopo + '/' + strItername+ '/' + strHost + '/nfd.log'
               (nTotalInterests, nOwnInterests) = readNfdLog(strNfdPath)
               newExp.nTotalInterests += nTotalInterests
               newExp.nConsumerInterests += nOwnInterests

            print('experiment=%s' % newExp.toString())



