'''
#Functionality test
#Description: Test connection, disconnection, confirming communication with stage,
#               inicialization(or something similar) and movement/position query
#               tests are successful and correct
'''

import sys
import unittest
import time #pylint: disable=unused-import
import ctypes #pylint: disable=unused-import
import pytest
pytestmark = pytest.mark.unit
from smc8 import SmcController as SMC #pylint: disable=C0413,E0401

##########################
## CONFIG
## connection and Disconnection in all test
###########################
class PhysicalTest(unittest.TestCase):
    '''physical test for Standa Attenuator'''

    #Instances for Test management
    def setUp(self):
        self.dev = None
        self.success = True
        self.device = ""
        self.log = False
        self.error_tolerance = 0.1
        self.device_connection = "192.168.29.123/9219"
        self.connection_type = "xinet"

    ##########################
    ## TestConnection and failure connection
    ##########################
    def test_connection(self):
        '''# Open connection'''
        self.dev = SMC()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type, log = self.log) # pylint: disable=C0301
        time.sleep(.25)
        assert self.dev.get_info()
        assert self.dev.serial_number is not None
        assert self.dev.power_setting is not None
        assert self.dev.device_information is not None
        #Close connection
        self.dev.disconnect()
        time.sleep(.25)

    def test_connection_failure(self):
        ''' Use an unreachable IP (TEST-NET-1 range, reserved for docs/testing)'''
        bad_connection = "dev/ximc/0000"
        self.dev = SMC()
        success = self.dev.connect(device_str = bad_connection, connection_type = self.connection_type, log = self.log) # pylint: disable=C0301
        self.assertFalse(success, "Expected connection failure with invalid IP/port")
        self.dev.disconnect()

    ##########################
    ## Status Communication
    ##########################
    def status_communication(self):
        '''Status gather testing'''
        # Open connection
        self.dev = SMC()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type, log = self.log) # pylint: disable=C0301
        time.sleep(.25)
        self.dev.get_info()
        status = self.dev.status()
        assert status is not None
        self.dev.disconnect()
        time.sleep(.25)

    ##########################
    ## Test Move and Home
    ##########################
    def test_home(self):
        '''Testing home and position query'''
        # Open connection
        self.dev = SMC()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type, log = self.log) # pylint: disable=C0301
        time.sleep(.25)
        assert self.dev.get_info()
        status = self.dev.status()
        assert status is not None
        assert self.dev.home()
        time.sleep(.25)
        pos = self.dev.get_pos()
        assert abs(pos - 0) < self.error_tolerance*2

        #Close connection
        self.dev.disconnect()
        time.sleep(.25)

    def test_move(self):
        '''Testing move and position query'''
        # Open connection
        self.dev = SMC()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type, log = self.log) # pylint: disable=C0301
        time.sleep(.2)
        assert self.dev.get_info()
        status = self.dev.status()
        assert status is not None
        assert self.dev.home()
        time.sleep(.25)
        pos = self.dev.get_pos()
        assert abs(pos - 0) < self.error_tolerance*2
        assert self.dev.set_pos(abs_move = True,position = 5)
        time.sleep(.25)
        pos = self.dev.get_pos()
        assert abs(pos - 5) < self.error_tolerance*2
        assert self.dev.set_pos(abs_move = False,position = 5)
        time.sleep(.25)
        pos = self.dev.get_pos()
        assert abs(pos - 10) < self.error_tolerance*2
        assert self.dev.home()
        time.sleep(.25)
        pos = self.dev.get_pos()
        assert abs(pos - 0) < self.error_tolerance*2
        #Close connection
        self.dev.disconnect()
        time.sleep(.25)

    def test_halt(self):
        '''Try to test halt but may not be able to do so without a more complex setup'''
        # Open connection
        self.dev = SMC()
        time.sleep(.2)
        self.dev.connect(device_str = self.device_connection, connection_type = self.connection_type, log = self.log) # pylint: disable=C0301
        time.sleep(.2)
        assert self.dev.get_info()
        status = self.dev.status()
        assert status is not None
        end = self.dev.max_limit - 1 
        assert self.dev.set_pos(abs_move = True,position = end)
        time.sleep(2)
        goal = self.dev.min_limit + 1
        assert self.dev.set_pos(abs_move = True,position = goal)
        assert self.dev.halt()
        time.sleep(.25)
        pos = self.dev.get_pos()
        assert pos != (self.dev.min_limit + 1)
        #Close connection
        self.dev.home()
        time.sleep(.25)
        self.dev.disconnect()
        time.sleep(.25)


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(PhysicalTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
