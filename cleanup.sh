#!/bin/bash

sudo mn -c
sudo killall -9 nfd
sudo killall -9 ndnputchunks
sudo killall -9 ndncatchunks
sudo service openvswitch-switch restart
sudo killall -9 ryu-manager
sudo rm -fr /tmp/icnsimulations/*
