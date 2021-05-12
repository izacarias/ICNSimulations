import matplotlib.pyplot as plt

c_strIcnSdnMarker = 'x'
c_strIpStpMarker  = '^'
c_strIpSdnMarker  = 's'
c_strIcnSdnColor = 'r'
c_strIpStpColor  = 'g'
c_strIpSdnColor  = 'b'

def delay_over_nodes(bAnnotate=True):

   # IP STP
   lstIpStpTimes = list()
   lstIpStpTimes.append((10, [30.38]))
   lstIpStpTimes.append((20, [51.48]))
   lstIpStpTimes.append((40, [95.77]))
   # lstIpStpTimes.append((60, [34852.47]))
   # lstIpStpTimes.append((80, [134411.50]))
   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((10, [24.42]))
   lstIpSdnTimes.append((20, [30.67]))
   lstIpSdnTimes.append((40, [34.2]))
   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((10, [18.79]))
   lstIcnSdnTimes.append((20, [19.62]))
   lstIcnSdnTimes.append((40, [17.96]))
   # lstIcnSdnTimes.append((80, []))

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

   plt.title('End to end delay RTT')
   plt.grid()
   plt.xlabel('Number of nodes')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()

def delay_over_cachePercentage(bAnnotate=True):

   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((0, [42.596, 62.99, 46.346]))
   lstIpSdnTimes.append((25, [26.68, 21.9, 21.97]))
   lstIpSdnTimes.append((50, [26.19, 21.78, 27.98]))
   lstIpSdnTimes.append((75, [23.5, 26.38, 20.98]))
   lstIpSdnTimes.append((100, [20.79, 26.52, 20.98]))
   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((0, [56.38, 51.48, 62.87, 49.24]))
   lstIcnSdnTimes.append((25, lstIcnSdnTimes[0][1]))
   lstIcnSdnTimes.append((50, lstIcnSdnTimes[0][1]))
   lstIcnSdnTimes.append((75, lstIcnSdnTimes[0][1]))
   lstIcnSdnTimes.append((100, lstIcnSdnTimes[0][1]))

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

   plt.plot(lstNodesIcnSdn, lstAvgsIcnSdn, marker=c_strIcnSdnMarker, color=c_strIcnSdnColor, markersize=6, label='ICN+SDN')
   plt.plot(lstNodesIpSdn, lstAvgsIpSdn, marker=c_strIpSdnMarker, color=c_strIpSdnColor, markersize=6, label='SDN')

   # plt.errorbar(x, y, yerr=yerr, color='r')

   plt.title('End to end delay over cache availability')
   plt.grid()
   plt.xlabel('Percentage of cache available (%)')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()

def delay_over_dataFlows(bAnnotate=True):

   t = 100
   p = 5
   nProd = 20
   nProduced = (t/p) * nProd

   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((nProduced*1, [56.38]))
   lstIpSdnTimes.append((nProduced*2, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*4, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*8, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*16, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*32, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*64, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*128, lstIpSdnTimes[0][1]))
   lstIpSdnTimes.append((nProduced*256, lstIpSdnTimes[0][1]))

   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((nProduced*1,   [44.53, 44.61, 44.50]))
   lstIcnSdnTimes.append((nProduced*2,   [50.00, 53.87, 47.92, 44.71]))
   lstIcnSdnTimes.append((nProduced*4,   [49.71, 43.96, 42.23, 41.67, 42.01]))
   lstIcnSdnTimes.append((nProduced*8,   [47.44, 42.30, 38.92, 38.04, 38.37]))
   lstIcnSdnTimes.append((nProduced*16,  [43.73, 42.10, 35.86, 35.33, 34.97]))
   lstIcnSdnTimes.append((nProduced*32,  [38.55, 39.51, 31.99, 31.89, 35.08]))
   lstIcnSdnTimes.append((nProduced*64,  [35.87, 29.09, 31.13, 29.04, 27.94]))
   lstIcnSdnTimes.append((nProduced*128, [26.47, 28.93, 27.13, 25.10, 24.43]))
   lstIcnSdnTimes.append((nProduced*256, [22.17, 23.74, 22.50, 22.91]))

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

   # plt.errorbar(x, y, yerr=yerr, color='r')

   plt.title('Delay over the number of data flows')
   plt.grid()
   plt.xlabel('Number of data flows')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()


if (__name__ == '__main__'):
   delay_over_nodes()
   # delay_over_cachePercentage()
   # delay_over_dataFlows()



'''
brokerColor = np.random.rand(3,)

        if (bShowByOrders):
            plt.plot_date(lstDates, lstRatioOrders, label=strLabel+' (Orders)', color=brokerColor, linestyle='solid', marker='x', markersize=7)
        if (bShowByAccounts):
            plt.plot_date(lstDates, lstRatioAccounts, label=strLabel+' (Accounts)', color=brokerColor, linestyle='solid', marker='s', markersize=5)

    plt.title('RAM usage ratio by number of accounts and orders')
    plt.xlabel('Time')
    plt.ylabel('RAM Usage ratio (MB/#accounts and MB/#orders)')
    plt.legend()
    plt.show()
'''
