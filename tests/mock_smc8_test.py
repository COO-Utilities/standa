
import pytest
pytestmark = pytest.mark.unit
import unittest
from unittest.mock import patch, MagicMock
# pylint: disable=import-error,no-name-in-module
from smc8 import SMC
import time

class TestSMC8(unittest.TestCase):
    """Unit tests for the SunpowerCryocooler class."""
    
    def setUp(self): # pylint: disable=arguments-differ
        """Set up the test case with a mocked ximc connection."""
        patcher = patch("smc8.ximc.Axis")  # <- patch the right function
        self.addCleanup(patcher.stop)
        mock_open_device = patcher.start()
        self.mock_ximc = MagicMock()
        mock_open_device.return_value = self.mock_ximc
        self.controller = SMC(ip="123.456.789.101", port=1234, log=False)
        self.controller.axis  = self.mock_ximc
        self.controller.dev_open = True
        self.controller.min_limit = 0.0
        self.controller.max_limit = 50.0
        self.mock_ximc.get_serial_number.return_value = 12345678
        self.mock_ximc.get_power_setting.return_value = 1
        self.mock_ximc.get_device_information.return_value = 5000
        self.mock_ximc.command_read_settings.return_value = 1000
        self.mock_ximc.command_homezero.return_value = True
        self.mock_ximc.get_position_calb.return_value = 0 , "0.0"
        self.mock_ximc.Position = 10.0

    def test_info(self):
        """Test getting the info from the attenuator."""
        assert self.controller.get_info()
        assert self.controller.serial_number is not None
        assert self.controller.power_setting is not None
        assert self.controller.device_information is not None
        assert self.controller.command_read_setting is not None
    

    def test_abs_move(self):
        """Testing sending the correct commands to abs move the SMC."""
        with patch.object(self.controller.axis, "command_move") as mock_move:
            self.controller.move_abs(10.0)
            mock_move.assert_called_once_with(10.0)
    
    def test_rel_move(self):
        """Testing sending the correct commands to rel move the SMC."""
        with patch.object(self.controller.axis, "command_movr") as mock_move:
            self.controller.move_rel(10.0)
            mock_move.assert_called_once_with(10.0)

    def test_home(self):
        """Test setting the position from the SMC."""
        with patch.object(self.controller.axis, "command_homezero") as mock_home:
            self.controller.home()
            mock_home.assert_called_once()

    def test_get_position(self):
        """Test getting the position from the SMC."""
        self.controller.axis.get_position_calb = MagicMock(return_value=self.mock_ximc)
        pos = self.controller.get_position()
        assert pos.Position == 10.0

    def test_get_status(self):
        """Test getting the status from the SMC."""
        self.controller.axis.get_status = MagicMock(return_value={"CurPosition" : 10.0, "CurSpeed" : 0.12 })
        status = self.controller.status()
        Position = status.CurPosition
        Moving_speed = status.CurSpeed
        assert Position is not None


if __name__ == "__main__":
    unittest.main()
    