'''
#Default Communication test
#Description: Test connection, disconnection and confirming communication with stage
'''

import sys
import unittest
import time #pylint: disable=unused-import
import ctypes #pylint: disable=unused-import
import pytest
pytestmark = pytest.mark.unit
from smc8 import SmcController #pylint: disable=C0413,E0401

pytestmark = pytest.mark.default

class ComTest(unittest.TestCase):
    '''Communication Test for Standa Attenuator'''

    #Instances for Test management
    #def setUp(self):
    dev = None
    success = True
    device = ""
    log = False
    error_tolerance = 0.1
    device_connection = "192.168.29.123/00009219"
    connection_type = "xinet"

    ##########################
    ## TestConnection and failure connection
    ##########################
    def test_connection(self):
        '''# Open connection    ''' 
        self.dev = SmcController()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type) # pylint: disable=C0301
        time.sleep(.25)
        assert self.dev.get_info()
        assert self.dev.serial_number is not None
        assert self.dev.power_setting is not None
        assert self.dev.device_information is not None
        #Close connection
        self.dev.disconnect()
        time.sleep(.25)

    def test_connection_failure(self):
        '''# Use an unreachable IP (TEST-NET-1 range, reserved for docs/testing)'''
        bad_connection = "dev/ximc/0000"
        self.dev = SmcController()
        time.sleep(.2)
        success = self.dev.connect(device_str = bad_connection, connection_type = self.connection_type) # pylint: disable=C0301
        self.assertFalse(success, "Expected connection failure with invalid IP/port")
        self.dev.disconnect()

    ##########################
    ## Status Communication
    ##########################
    def status_communication(self):
        '''Status retrieval test'''
        self.dev = SmcController()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type) # pylint: disable=C0301
        time.sleep(.25)
        assert self.dev.get_info()
        status = self.dev.status()
        assert status is not None

        self.dev.disconnect()
        time.sleep(.25)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ComTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
