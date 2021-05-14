#!/bin/python

from os.path import dirname, basename

inFile = open('/home/vagrant/nfdlogs/out.txt')
lstLines = inFile.readlines()

lst10 = list()
lst20 = list()
lst30 = list()
lst40 = list()
for strLine in lstLines:
   if (strLine.find('wifi-topo10.conf') > 0):
      lst10.append(strLine)
   elif (strLine.find('wifi-topo20.conf') > 0):
      lst20.append(strLine)
   elif (strLine.find('wifi-topo30.conf') > 0):
      lst30.append(strLine)
   elif (strLine.find('wifi-topo40.conf') > 0):
      lst40.append(strLine)

inFile.close()

lstTopos = [lst10, lst20, lst30, lst40]
outFile = open('/home/vagrant/processed_out.txt', 'w')

nAcum = 0
nCount = 0
for lstTopo in lstTopos:
   outFile.write('\n-------------------------------------\n')

   curExpPath = ''
   for (nIndex, strLine) in enumerate(lstTopo):

      strDirname = dirname(strLine[0:strLine.find(':')])
      expPath = dirname(strDirname)

      print('expPath=%s' % expPath)

      if (curExpPath == ''):
         curExpPath = expPath

      # print('line: %s, exp=%s; lastExp=%s' % (strLine.strip(), expPath, curExpPath))
      if (nIndex == (len(lstTopo) - 1)):
         # print('List done')
         outFile.write('%s : Acum=%d; Count=%d\n' % (expPath, nAcum, nCount))
         nAcum = 0
         nCount = 0
         curExpPath = ''
      elif (expPath != curExpPath):
         # Dir changed
         print('Changed lastExp=%s; newExp=%s, nCount=%d, ' % (curExpPath, expPath, nCount))
         outFile.write('%s : Acum=%d; Count=%d\n' % (curExpPath, nAcum, nCount))
         nAcum = int(strLine[strLine.find(':')+1:])
         nCount = 1
         curExpPath = expPath
      else:
         # Still same dir
         # print('Still same')
         nAcum += int(strLine[strLine.find(':')+1:])
         nCount += 1

outFile.close()
