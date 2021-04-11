#!/bin/bash

MININDN_DIR="/home/vagrant/mini-ndn"
PARENT_PATH=$(dirname "${BASH_SOURCE[0]}")

# Consumer and producer
cp $PARENT_PATH/producer.cpp $MININDN_DIR/ndn-src/ndn-cxx/examples/
cp $PARENT_PATH/consumer.cpp $MININDN_DIR/ndn-src/ndn-cxx/examples/
cp $PARENT_PATH/consumer-with-timer.cpp $MININDN_DIR/ndn-src/ndn-cxx/examples/

# Gambi
cd $PARENT_PATH; cd ..; ./build.sh


echo "Done"

