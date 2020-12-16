"""
This script generates the data queue use by ICN simulations.

Created 16/12/2020 by Andre Dexheimer Carneiro
"""
from data_manager import DataManager
import pickle
import logging


# ---------------------------------------- Constants
c_strLogFile         = './generate_data_queue.log'
c_nMissionMinutes    = 5

logging.basicConfig(filename=c_strLogFile, format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():
    """
    Generates a data queue saved with pickle which can be read by ICN experiments.
    """



if __name__ == '__main__':
    main()