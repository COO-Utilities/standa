#################
#Unit test
#Description: Validate software functions are correctly implemented via mocking
#################
import unittest
from unittest.mock import patch, MagicMock
import time #pylint: disable=unused-import
import ctypes #pylint: disable=unused-import
import pytest
pytestmark = pytest.mark.unit
from smc8 import SmcController as SMC #pylint: disable=C0413,E0401

class TestSMC8(unittest.TestCase):
    """Unit tests for the SunpowerCryocooler class."""

    def setUp(self): # pylint: disable=arguments-differ
        """Set up the test case with a mocked ximc connection."""
        patcher = patch("smc8.ximc.Axis")  # <- patch the right function
        self.addCleanup(patcher.stop)
        mock_open_device = patcher.start()
        self.mock_ximc = MagicMock()
        mock_open_device.return_value = self.mock_ximc
        self.controller = SMC() #pylint: disable=C0301
        self.controller._axis  = self.mock_ximc # pylint: disable=protected-access
        self.controller.dev_open = True
        self.controller.min_limit = -500
        self.controller.max_limit = 500
        self.mock_ximc.get_serial_number.return_value = 12345678
        self.mock_ximc.get_power_setting.return_value = 1
        self.mock_ximc.get_device_information.return_value = 5000
        self.mock_ximc.command_homezero.return_value = True
        self.mock_ximc.get_position_calb.return_value = 0 , "0.0"
        self.mock_ximc.Position = 10
        self.mock_ximc.CurPosition = 10
        self.mock_ximc.CurSpeed = 0.12

    def test_info(self):
        """Test getting the info from the attenuator."""
        assert self.controller.get_info()
        assert self.controller.serial_number is not None
        assert self.controller.power_setting is not None
        assert self.controller.device_information is not None


    def test_abs_move(self):
        """Testing sending the correct commands to abs move the SMC."""
        mock_axis = MagicMock()
        self.controller._axis = mock_axis  # pylint: disable=protected-access

        self.controller.move_abs(10)
        mock_axis.command_move.assert_called_once_with(10,0)

    def test_rel_move(self):
        """Testing sending the correct commands to rel move the SMC."""
        mock_axis = MagicMock()
        self.controller._axis = mock_axis  # pylint: disable=protected-access
        self.controller.get_position = MagicMock(return_value=0)

        self.controller.move_rel(10)
        mock_axis.command_movr.assert_called_once_with(10,0)

    def test_home(self):
        """Test setting the position from the SMC."""
        with patch.object(self.controller._axis, "command_homezero") as mock_home: # pylint: disable=protected-access
            self.controller.home()
            mock_home.assert_called_once()

    def test_get_position(self):
        """Test getting the position from the SMC."""
        self.controller._axis.get_position = MagicMock(return_value=self.mock_ximc) # pylint: disable=protected-access
        pos = self.controller.get_position()
        assert pos == 10

    def test_get_status(self):
        """Test getting the status from the SMC."""
        self.controller._axis.get_status = MagicMock(return_value=self.mock_ximc) # pylint: disable=protected-access
        status = self.controller.status()
        position = status.CurPosition
        moving_speed = status.CurSpeed
        assert position is not None


if __name__ == "__main__":
    unittest.main()
