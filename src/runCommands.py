import subprocess

lstHosts = ['ap_h0', 'ap_h1', 'ap_h2', 'ap_h3', 'ap_d0', 'ap_d1', 'ap_d2', 'ap_v0', 'ap_v1']

# for strHost in lstHosts:
#    subprocess.call(['ovs-vsctl', 'set-controller', strHost, 'tcp:127.0.0.1:6633'])


nApId = 1
for strAp in lstHosts:
   strApId = '1000000000' + str(nApId).zfill(6)
   subprocess.call(['ovs-vsctl', 'set-controller', strAp, 'tcp:127.0.0.1:6633'])
   subprocess.call(['ovs-vsctl', 'set', 'bridge', strAp, 'other-config:datapath-id='+strApId])
   nApId += 1

   