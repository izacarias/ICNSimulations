import subprocess as sp
import re


def main():

   lstAps = ['ap_h0', 'ap_d0', 'ap_v0']

   hshAps = collectRules(lstAps)
   for strAp in hshAps:
      print('------------------list for ap=%s\n%s' % (strAp, str(hshAps[strAp])))

   applyRules(hshAps)

   # Rule Collector
   # Run for at least about 20 seconds
   # Once past that threshold, keep running while more rules are still being collected for any APs
      # New rules must be compared with the old ones in case they are just being reordered in the list
   # When rules stabilize for a certain time window, save everything into a file that can be read before the experiment starts 

def collectRules(lstAps):
   """
   Collects forwarding rules from all APs given and returns them in the form of a 
   dictionary with all the APs names and lists containing each rule.
   """
   hshNodes = {}
   for pAp in lstAps:
      strAp = str(pAp)
      hshNodes[strAp] = list()
      proc = sp.Popen(['ovs-ofctl', 'dump-flows', strAp], stdout=sp.PIPE)
      # Extract only stdout from index 0
      strOut = proc.communicate()[0]
      # Remove whitespace characters
      rules = strOut.replace(' ', '')
      # Extract each line as a separate rule
      rules = rules.split('\n')
      # Remove nodes 'NXST_FLOW reply (xid=0x4):' from position 0 and empty string from the last position
      rules = rules[1:-1]
      # Add comma before 'actions='
      for strRule in rules:
         nIndex = strRule.index('actions')
         strRule = strRule[:nIndex] + ',' + strRule[nIndex:]
         strRule = replaceTimeouts(strRule)
         hshNodes[strAp].append(strRule)
   return hshNodes

def applyRules(hshAps):

   for strAp in hshAps:
      for strRule in hshAps[strAp]:
         sp.call(['ovs-ofctl', 'add-flow', strAp, strRule])

def replaceTimeouts(strRule):
   """
   Replaces values for idle_timeout and hard_timeout with obscenely large values.
   """
   # c_strDefaultIdle = '10'
   # c_strDefaultHard = '30'
   # strRule = strRule.replace('idle_timeout=10', 'idle_timeout=200000')
   # strRule = strRule.replace('hard_timeout=30', 'hard_timeout=200000')
   strRule = re.sub(r'idle_timeout=\d+', 'idle_timeout=60000', strRule)
   strRule = re.sub(r'hard_timeout=\d+', 'hard_timeout=60000', strRule)
   return strRule

if (__name__ == '__main__'):
   main()