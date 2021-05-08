#!/bin/bash

n_iterations=3
flag_run_icn=0
flag_run_ip=0
experiment_time=200
username="vagrant"
output_dir="/home/vagrant/try1"
log_path="./experiment.log"

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
    date >> $log_path
    echo "Running $2 experiment for topo $1, iteration $3" >> $log_path

    cd controller
    if [ "$2" = "icn" ] || [ "$2" = "ip" ]; then
      ./IPController.sh &

    else
      ./SDNController.sh &
    fi
    cd -

    sudo python notcomplex-wifi.py -t $experiment_time --topo $1 --$2
    exit
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
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "ip" 1
run_benchmark "/home/vagrant/icnsimulations/topologies/experiment/wifi-topo20.conf" "ip_sdn" 2

echo "Done!" >> $log_path