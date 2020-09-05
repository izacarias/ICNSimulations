#!/bin/bash

MININDN_DIR="/home/osboxes/mini-ndn"
PARENT_PATH=$(dirname "${BASH_SOURCE[0]}")

# Copy experiment and dependencies
cp $PARENT_PATH/random_talks.py $MININDN_DIR/ndn/experiments/
cp $PARENT_PATH/DataManager.py $MININDN_DIR/ndn/experiments/

# Install experiment
cd $MININDN_DIR; ./install.sh -i

# https://github.com/philoL/minindn-deployment/blob/master/docs/EXPERIMENTS.md