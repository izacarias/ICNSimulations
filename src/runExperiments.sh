#!/bin/bash

n_iterations=3
flag_run_icn=0
flag_run_ip=0
experiment_time=100
username="vagrant"
output_dir="/home/vagrant/try6_cache_loss"
log_path="./experiment.log"
experiment_log_path="./runtime.log"


cleanup () {
  sudo mn -c
  sudo killall -9 nfd
  sudo killall -9 ndnputchunks
  sudo killall -9 ndncatchunks
  sudo service openvswitch-switch restart
  sudo killall -9 ryu-manager
  sudo rm -fr /tmp/icnsimulations/*
}

run_benchmark () {
    # $1 -> topology path
    # $2 -> experiment type (icn_sdn, ip, ip_sdn)
    # $3 -> experiment iteration
    # $4 -> cache ratio
    date >> $log_path
    date >> $experiment_log_path
    echo "Running $2 experiment for topo $1, iteration $3, cache ratio $4" >> $log_path

    cd controller
    if [ "$2" = "icn" ] || [ "$2" = "ip" ]; then
      ./IPController.sh &

    else
      ./SDNController.sh &
    fi
    cd -

    sudo python ./notcomplex-wifi.py -t $experiment_time --topo $1 --$2 --cache-ratio=$4 >> $experiment_log_path
    python ./read_nfd_results.py $1 >> $log_path
    for host_dir in $(ls /tmp/icnsimulations)
    do
        log_output=$output_dir/$2/$(basename $1)/run$3/$host_dir
        mkdir -p $log_output
        sudo mv /tmp/icnsimulations/$host_dir/nfd.log $log_output
        sudo chmod -R 755 $output_dir/$1/run$2/$host_dir
    done

    cp ../log/experiment_send.log $output_dir/$2/$(basename $1)/run$2
    sudo chown -R $username $output_dir
    cleanup
}

cleanup
# BENCHMARK FOR CACHE RATIO
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 0_1 0.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 0_2 0.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 0_3 0.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 025_1 0.25
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 025_2 0.25
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 025_3 0.25
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 05_1 0.5
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 05_2 0.5
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 05_3 0.5
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 075_1 0.75
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 075_2 0.75
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 075_3 0.75
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 1_1 1.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 1_2 1.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "icn_sdn" 1_3 1.0

# BENCHMARK FOR NETWORK LOSS

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20_10loss.conf" "icn_sdn" 10loss1 1.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20_20loss.conf" "icn_sdn" 20loss1 1.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20_30loss.conf" "icn_sdn" 30loss1 1.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20_40loss.conf" "icn_sdn" 40loss1 1.0
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20_50loss.conf" "icn_sdn" 50loss1 1.0

exit

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "ip" 1
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "ip" 2
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "ip" 3

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo40.conf" "ip" 1

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo40.conf" "icn_sdn" 1

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo60.conf" "ip" 1
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo60.conf" "icn_sdn" 1

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo80.conf" "ip" 1
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo80.conf" "icn_sdn" 1

run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo100.conf" "ip" 1
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo100.conf" "icn_sdn" 1

echo "Done!" >> $log_path
