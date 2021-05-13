import matplotlib.pyplot as plt

c_strIcnSdnMarker = 'x'
c_strIpStpMarker  = '^'
c_strIpSdnMarker  = 's'
c_strIcnSdnColor = 'r'
c_strIpStpColor  = 'g'
c_strIpSdnColor  = 'b'

def delay_over_nodes(bAnnotate=True, bShowLegend=False):

   # IP STP
   lstIpStpTimes = list()
   lstIpStpTimes.append((10, [30.38]))
   lstIpStpTimes.append((20, [51.48]))
   lstIpStpTimes.append((30, [87.84]))
   lstIpStpTimes.append((40, [97.57]))
   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((10, [24.42]))
   lstIpSdnTimes.append((20, [30.67]))
   lstIpSdnTimes.append((30, [24.68]))
   lstIpSdnTimes.append((40, [30.65]))
   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((10, [18.79]))
   lstIcnSdnTimes.append((20, [19.62]))
   lstIcnSdnTimes.append((30, [15.88]))
   lstIcnSdnTimes.append((40, [17.03]))

   # Calculate averages
   lstNodesIpStp = list()
   lstAvgsIpStp = list()
   for (nNodes, lstTimes) in lstIpStpTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpStp.append(nNodes)
      lstAvgsIpStp.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nNodes, sAvg))

   # Calculate averages
   lstNodesIpSdn = list()
   lstAvgsIpSdn = list()
   for (nNodes, lstTimes) in lstIpSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpSdn.append(nNodes)
      lstAvgsIpSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nNodes, sAvg))

   # Calculate averages
   lstNodesIcnSdn = list()
   lstAvgsIcnSdn = list()
   for (nNodes, lstTimes) in lstIcnSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIcnSdn.append(nNodes)
      lstAvgsIcnSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nNodes, sAvg))

   plt.plot(lstNodesIcnSdn, lstAvgsIcnSdn, marker=c_strIcnSdnMarker, color=c_strIcnSdnColor, markersize=6, label='ICN+SDN')
   plt.plot(lstNodesIpStp, lstAvgsIpStp, marker=c_strIpStpMarker, color=c_strIpStpColor, markersize=6, label='IP')
   plt.plot(lstNodesIpSdn, lstAvgsIpSdn, marker=c_strIpSdnMarker, color=c_strIpSdnColor, markersize=6, label='SDN')

   # plt.errorbar(x, y, yerr=yerr, color='r')

   if (bShowLegend):
      plt.title('End to end delay RTT')
   plt.grid()
   plt.xlabel('Número de nós da rede')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()

def delay_over_cachePercentage(bAnnotate=True, bShowTitle=False):

   # IP
   lstIpStpTimes = list()
   lstIpStpTimes.append((0, [51.48]))
   lstIpStpTimes.append((25, lstIpStpTimes[0][1]))
   lstIpStpTimes.append((50, lstIpStpTimes[0][1]))
   lstIpStpTimes.append((75, lstIpStpTimes[0][1]))
   lstIpStpTimes.append((100, lstIpStpTimes[0][1]))
   # IP SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((0, [47.02]))
   lstIcnSdnTimes.append((25, [26.68, 21.9, 21.97]))
   lstIcnSdnTimes.append((50, [26.19, 21.78, 27.98]))
   lstIcnSdnTimes.append((75, [23.5, 26.38, 20.98]))
   lstIcnSdnTimes.append((100, [20.79, 26.52, 20.98]))
   # ICN SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((0, [46.52]))
   lstIpSdnTimes.append((25, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((50, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((75, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((100, lstIpSdnTimes[0][1]))

   # Calculate averages
   lstNodesIpStp = list()
   lstAvgsIpStp = list()
   for (nPercentage, lstTimes) in lstIpStpTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpStp.append(nPercentage)
      lstAvgsIpStp.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nPercentage, sAvg))

   # Calculate averages
   lstNodesIpSdn = list()
   lstAvgsIpSdn = list()
   for (nPercentage, lstTimes) in lstIpSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpSdn.append(nPercentage)
      lstAvgsIpSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nPercentage, sAvg))

   # Calculate averages
   lstNodesIcnSdn = list()
   lstAvgsIcnSdn = list()
   for (nPercentage, lstTimes) in lstIcnSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIcnSdn.append(nPercentage)
      lstAvgsIcnSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nPercentage, sAvg))

   plt.plot(lstNodesIpStp, lstAvgsIpStp, marker=c_strIpStpMarker, color=c_strIpStpColor, markersize=6, label='IP')
   plt.plot(lstNodesIpSdn, lstAvgsIpSdn, marker=c_strIpSdnMarker, color=c_strIpSdnColor, markersize=6, label='SDN')
   plt.plot(lstNodesIcnSdn, lstAvgsIcnSdn, marker=c_strIcnSdnMarker, color=c_strIcnSdnColor, markersize=6, label='ICN+SDN')

   # plt.errorbar(x, y, yerr=yerr, color='r')

   if (bShowTitle):
      plt.title('End to end delay over cache availability')
   plt.grid()
   plt.xlabel('Percentual de cache disponível (%)')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()

def delay_over_dataFlows(bAnnotate=True, bShowTitle=False):

   t = 100
   p = 5
   nProd = 20
   nProduced = (t/p) * nProd

   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((nProduced*1, [46.2]))
   lstIpSdnTimes.append((nProduced*4, [47.4]))
   lstIpSdnTimes.append((nProduced*32, [40.82]))
   lstIpSdnTimes.append((nProduced*128, [42.3]))
   lstIpSdnTimes.append((nProduced*256, [43.4]))

   # IP
   lstIpStpTimes = list()
   lstIpStpTimes.append((nProduced*1, [56.72]))
   lstIpStpTimes.append((nProduced*4, [55.34]))
   lstIpStpTimes.append((nProduced*32, [49.23]))
   lstIpStpTimes.append((nProduced*128, [51.12]))
   lstIpStpTimes.append((nProduced*256, [51.31]))

   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((nProduced*1,   [44.53, 44.61, 44.50]))
   lstIcnSdnTimes.append((nProduced*4,   [49.71, 43.96, 42.23, 41.67, 42.01]))
   lstIcnSdnTimes.append((nProduced*8,   [47.44, 42.30, 38.92, 38.04, 38.37]))
   lstIcnSdnTimes.append((nProduced*16,  [43.73, 42.10, 35.86, 35.33, 34.97]))
   lstIcnSdnTimes.append((nProduced*32,  [38.55, 39.51, 31.99, 31.89, 35.08]))
   lstIcnSdnTimes.append((nProduced*64,  [35.87, 29.09, 31.13, 29.04, 27.94]))
   lstIcnSdnTimes.append((nProduced*128, [26.47, 28.93, 27.13, 25.10, 24.43]))
   lstIcnSdnTimes.append((nProduced*256, [22.17, 23.74, 22.50, 22.91]))

   # Calculate averages
   lstNodesIpStp = list()
   lstAvgsIpStp = list()
   for (nDataFlows, lstTimes) in lstIpStpTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpStp.append(nDataFlows)
      lstAvgsIpStp.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nDataFlows, sAvg))

   # Calculate averages
   lstNodesIpSdn = list()
   lstAvgsIpSdn  = list()
   for (nDataFlows, lstTimes) in lstIpSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpSdn.append(nDataFlows)
      lstAvgsIpSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nDataFlows, sAvg))

   # Calculate averages
   lstNodesIcnSdn = list()
   lstAvgsIcnSdn = list()
   for (nDataFlows, lstTimes) in lstIcnSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIcnSdn.append(nDataFlows)
      lstAvgsIcnSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f ms' % sAvg, xy=(nDataFlows, sAvg))

   plt.plot(lstNodesIcnSdn, lstAvgsIcnSdn, marker=c_strIcnSdnMarker, color=c_strIcnSdnColor, markersize=6, label='ICN+SDN')
   plt.plot(lstNodesIpSdn, lstAvgsIpSdn, marker=c_strIpSdnMarker, color=c_strIpSdnColor, markersize=6, label='SDN')
   plt.plot(lstNodesIpStp, lstAvgsIpStp, marker=c_strIpStpMarker, color=c_strIpStpColor, markersize=6, label='IP')

   # plt.errorbar(x, y, yerr=yerr, color='r')

   if (bShowTitle):
      plt.title('Delay over the number of data flows')
   plt.grid()
   plt.xlabel('Número de fluxos de dados')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()

def interests_over_nodes(bAnnotate=True, bShowLegend=False):
   # IP STP
   lstIpStpTimes = list()
   lstIpStpTimes.append((10, [6963]))
   lstIpStpTimes.append((20, [44507]))
   lstIpStpTimes.append((40, [224780]))
   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((10, [7341]))
   lstIpSdnTimes.append((20, [44996]))
   lstIpSdnTimes.append((40, [222995]))
   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((10, [3710]))
   lstIcnSdnTimes.append((20, [23774]))
   lstIcnSdnTimes.append((40, [121427]))

   # Calculate averages
   lstNodesIpStp = list()
   lstAvgsIpStp = list()
   for (nNodes, lstTimes) in lstIpStpTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpStp.append(nNodes)
      lstAvgsIpStp.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f' % sAvg, xy=(nNodes, sAvg))

   # Calculate averages
   lstNodesIpSdn = list()
   lstAvgsIpSdn = list()
   for (nNodes, lstTimes) in lstIpSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIpSdn.append(nNodes)
      lstAvgsIpSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f' % sAvg, xy=(nNodes, sAvg))

   # Calculate averages
   lstNodesIcnSdn = list()
   lstAvgsIcnSdn = list()
   for (nNodes, lstTimes) in lstIcnSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIcnSdn.append(nNodes)
      lstAvgsIcnSdn.append(sAvg)
      if (bAnnotate):
         plt.annotate('%.2f' % sAvg, xy=(nNodes, sAvg))

   plt.plot(lstNodesIcnSdn, lstAvgsIcnSdn, marker=c_strIcnSdnMarker, color=c_strIcnSdnColor, markersize=6, label='ICN+SDN')
   plt.plot(lstNodesIpSdn, lstAvgsIpSdn, marker=c_strIpSdnMarker, color=c_strIpSdnColor, markersize=6, label='SDN')
   plt.plot(lstNodesIpStp, lstAvgsIpStp, marker=c_strIpStpMarker, color=c_strIpStpColor, markersize=6, label='IP')

   # plt.errorbar(x, y, yerr=yerr, color='r')

   if (bShowLegend):
      plt.title('Number of outgoing interests')
   plt.grid()
   plt.xlabel('Número de nós da rede')
   plt.ylabel('Requisições de interesse')
   plt.legend()
   plt.show()

if (__name__ == '__main__'):
   # delay_over_nodes(bAnnotate=False)
   # delay_over_cachePercentage(bAnnotate=False)
   delay_over_dataFlows(bAnnotate=False)
   # interests_over_nodes(bAnnotate=False)
