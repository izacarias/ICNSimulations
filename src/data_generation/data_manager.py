"""
Creates and manages Command And Control (C2) package types and
package queues.

Created 25/09/2020 by Andre Dexheimer Carneiro
"""
import logging
from c2_datatype import C2DataType

# logging.basicConfig(filename="DataManager.log", format='%(asctime)s %(message)s', level=logging.DEBUG)

class DataManager:

    def __init__(self):
        """
        Constructor
        """
        self.lstDataTypes = []
        # Initialize known dataTypes
        self.lstDataTypes.append(C2DataType(nTTL=10000, nPeriod=20, nType=1, nSize=5000,
            lstAllowedHostTypes=['d', 'h', 'v', 's'], sRatioMaxReceivers=100, sPeriodWiggleRoom=0.2))   # INTEREST 1

    def generateSpreadDataQueue(self, lstHosts, nMissionMinutes):
        """
        Generates a simple data queue for spreading packets from only one node.
        """
        lstDataQueue = []
        if (len(lstHosts) > 0):
            strHost = lstHosts[0]
            self.lstDataTypes[0].generateSpreadDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)

        return lstDataQueue

    def generateDataQueue(self, lstHosts, nMissionMinutes):
        """
        Generates an unordered queue with packages and send time
        """
        lstDataQueue = []
        for strHost in lstHosts:
            # Generate data from each host
            if(strHost[0] == 'd'):
                # Drone
                logging.info('[generateDataQueue] Node type drone, strHost=%s' % (strHost))
                self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 'h'):
                # Human
                logging.info('[generateDataQueue] Node type human, strHost=%s' % (strHost))
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 's'):
                # Sensor
                logging.info('[generateDataQueue] Node type sensor, strHost=%s' % (strHost))
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            elif(strHost[0] == 'v'):
                # Vehicle
                logging.info('[generateDataQueue] Node type vehicle, strHost=%s' % (strHost))
                # self.lstDataTypes[0].generateDataQueue(strHost, nMissionMinutes, lstDataQueue, lstHosts)
            else:
                # Unrecognized host type
                logging.error('[generateDataQueue] Unrecognized host type ' + strHost)

        lstDataQueue.sort(key=lambda x: x[0])
        return lstDataQueue

    def getTTLValuesParam(self):
        """
        Returns a string listing the TTL values for all available data types
        """
        strTTLValues = ''
        for DataType in self.lstDataTypes:
            strTTLValues += str(DataType.nTTL/1000) + ' '
        # Remove last whitespace
        strTTLValues = strTTLValues[:-1]
        return strTTLValues

    def getPayloadValuesParam(self):
        """
        Returns a string listing the payload values for all available data types
        """
        strPayloadValues = ''
        for DataType in self.lstDataTypes:
            strPayloadValues += str(DataType.nPayloadSize) + ' '
        # Remove last whitespace
        strPayloadValues = strPayloadValues[:-1]
        return strPayloadValues



if (__name__ == '__main__'):
    main()
