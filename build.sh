#!/bin/bash

MININDN_DIR="/home/vagrant/mini-ndn"

cd $MININDN_DIR/ndn-src/ndn-cxx/; ./waf configure --with-examples; sudo ./waf
cd $MININDN_DIR/ndn-src/ndn-cxx/; sudo ./waf
cd /usr/bin; sudo ln -s $MININDN_DIR/ndn-src/ndn-cxx/build/examples/producer producer
cd /usr/bin; sudo ln -s $MININDN_DIR/ndn-src/ndn-cxx/build/examples/consumer consumer
cd /usr/bin; sudo ln -s $MININDN_DIR/ndn-src/ndn-cxx/build/examples/consumer-with-timer consumer-with-timer
cd /usr/bin; sudo ln -s $MININDN_DIR/ndn-src/ndn-cxx/build/examples/consumer-with-queue consumer-with-queue
