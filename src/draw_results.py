import matplotlib.pyplot as plt

def main():

   # IP STP
   lstIpStpTimes = list()
   lstIpStpTimes.append((20, [132.32, 97.62, 116.43]))
   lstIpStpTimes.append((40, [1358.47]))
   # lstIpStpTimes.append((60, [34852.47]))
   # lstIpStpTimes.append((80, [134411.50]))
   # IP SDN
   lstIpSdnTimes = list()
   lstIpSdnTimes.append((20, [56.38, 51.46]))
   lstIpSdnTimes.append((40, [721.32]))
   # ICN SDN
   lstIcnSdnTimes = list()
   lstIcnSdnTimes.append((20, [23.74, 23.95, 25.66]))
   lstIcnSdnTimes.append((40, [40.48]))
   lstIcnSdnTimes.append((60, [40.33]))
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
      plt.annotate('%.2f ms' % sAvg, xy=(nNodes, sAvg))

   lstNodesIcnSdn = list()
   lstAvgsIcnSdn = list()
   for (nNodes, lstTimes) in lstIcnSdnTimes:
      sAvg = 0
      if (len(lstTimes) > 0):
         sAvg = sum(lstTimes)/len(lstTimes)
      lstNodesIcnSdn.append(nNodes)
      lstAvgsIcnSdn.append(sAvg)
      plt.annotate('%.2f ms' % sAvg, xy=(nNodes, sAvg))

   plt.plot(lstNodesIcnSdn, lstAvgsIcnSdn, marker='x', markersize=6, label='ICN+SDN')
   plt.plot(lstNodesIpStp, lstAvgsIpStp, marker='^', markersize=6, label='IP')
   plt.plot(lstNodesIpSdn, lstAvgsIpSdn, marker='s', markersize=6, label='SDN')

   # plt.errorbar(x, y, yerr=yerr, color='r')

   # brokerColor = np.random.rand(3,)

   plt.title('End to end delay RTT')
   plt.grid()
   plt.xlabel('Number of nodes')
   plt.ylabel('Delay (ms)')
   plt.legend()
   plt.show()

if (__name__ == '__main__'):
   main()



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
