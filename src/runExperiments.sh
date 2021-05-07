#!/bin/bash

./controller/IPController.sh &
sudo python ./notcomplex-wifi.py -t ../topologies/experiment/wifi-topo20.conf