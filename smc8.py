'''
    standa.smc8.py: Class for controlling Standa SMC motion controllers
    using the libximc library.
    NOTE:: Pip install of libximc is needed to use the library imported
       These are not standard python librarys but are on PyPI
                       -Elijah Anakalea-Buckley
'''
from typing import Tuple, Union, Dict
import libximc.highlevel as ximc
from hardware_device_base import HardwareMotionBase

class SmcController(HardwareMotionBase):
    ''' 
        Class is for utilizing the libximc Library.
        Functions from lib.ximc are incorporated into this class
        to make it easier to use for common tasks.
        - using the more recently developed libximc.highlevel API
        - step_size:float = 0.0025 Conversion Coefficient, Example  for
            converting steps to mm used in API, adjust as needed
        - All functions log their actions and errors to a log file
        - Required Parameters:
            device_str: str = Connection string for device
                - Ex: serial connection: '/COM3', '/dev/ximc/000746D30' or '192.123.123.92'
                - NOTE:: For Network you must provide IP/Name and device ID. Device ID is the 
                            serial number tranlslated to hex
                        EX: SMC(device_str = "192.168.29.123/9219", connection_type="xinet")
            connection_type: str = Type of connection
                - Options: 'serial'=USB, 'tcp'=Raw TCP, 'xinet'=Network
            log: bool = Enable or disable logging to file
    '''

    _move_cmd_flags = ximc.MvcmdStatus  # Default move command flags
    _state_flags = ximc.StateFlags

    def __init__(self, log:bool=True, logfile: str =__name__.rsplit(".", 1)[-1]):
        '''
            Inicializes the device
            parameters: ip string, port integer, logging bool
            - full device capabilities will be under "self.device.<functions()>"


            connection_type: str="serial", step_size:float = 0.0025
        '''
        super().__init__(log, logfile)
        #Inicialize variables and objects
        self.serial_number = None
        self.power_setting = None
        self.device_information = None
        self._engine_settings = None
        self.min_limit = None
        self.max_limit = None
        self._homed_and_happy_bool = False
        self._uPOSITION = 0 #Constant is 0 for DC motors and avaries for stepper motors (pylint: disable=C0103)
                           #look into ximc library for details on uPOSITION
        self.device_uri = None
        self.dev_open = False
        self.step_size_coeff = None
        self._axis = None

    def connect(self, connection_type: str, device_str: str, step_size:float = 0.0025): # pylint: disable=W0221
        '''
            Opens communication to the Device, gathers general information to 
            store in local variables.
            - Reference for connecting to device
            - device_uri = r"xi-emu:///ABS_PATH/virtual_controller.bin" # Virtual device
            - device_uri = r"xi-com:\COM111"                            # Serial port
            - device_uri = "xi-tcp://172.16.130.155:1820"               # Raw TCP connection
            - device_uri = "xi-net://192.168.1.120/abcd"                # XiNet connection
            return: Bool for successful or unsuccessful connection
            libximc:: open_device()
        '''
        #Check if already open
        if self.dev_open:
            #log that device is already open
            self.report_info("Device already open, skipping open command.")
            #return true if already open
            return True
        #try to open
        try:
            #Build device URI based on connection type
            connection_type = connection_type.lower().strip()
            if connection_type == "serial":
                self.device_uri = f"xi-com://{device_str}"
            elif connection_type == "tcp":
                self.device_uri = f"xi-tcp://{device_str}"
            elif connection_type == "xinet":
                self.device_uri = f"xi-net://{device_str}"
            else:
                self.report_error(f"Unknown connection type: {connection_type}")
                raise ValueError(f"Unknown connection type: {connection_type}")


            self.step_size_coeff = step_size  # Example conversion coefficient, adjust as needed(mm)
            #open device
            self._axis =ximc.Axis(self.device_uri)
            self._axis.open_device()
            #get and save engine settings
            self._engine_settings = self._axis.get_engine_settings()
            #Set calb for user units(SPECIFICALLY THE MICROSTEP MODE)
            self._axis.set_calb(self.step_size_coeff, self._engine_settings.MicrostepMode)
            self.get_limits()

            self.report_info("Device opened successfully.")

            #return true if successful
            self.dev_open = True
        except ValueError as e:
            #log error
            self.report_error(f"Error opening device: {e}")
            self.dev_open = False
        except ConnectionError as e:
            #log error
            self.report_error(f"Connection error opening device: {e}")
            self.dev_open = False
        except Exception as e: #pylint: disable=W0718
            #log error
            self.report_error(f"Unknown error opening device: {e}")
            self.dev_open = False
        return self.dev_open

    def disconnect(self):
        '''
            Closes communication to the Device
            return: Bool for successful or unsuccessful termination
            libximc:: close_device()
        '''
        #Check if already open
        if not self.dev_open:
            #log that device is closed
            self.report_warning("Already disconnected from device.")
            return True

        #Try to close, return result
        try:
            self._axis.close_device()
            self.dev_open = False
            self.report_info("Device closed successfully.")
            return True
        except Exception as e: #pylint: disable=W0718
            #log error and return device still open
            self.report_error(f"Error closing device: {e}")
            self.dev_open = True
            return False

    def get_info(self):
        '''
            Gets information about the device, such as serial number, power setting,
            command read settings, and device information. That information is stored
            in local variables for later use.
            - This function is called after opening the device to gather information
            return: dict with device information
            libximc:: get_serial_number(), get_power_setting(), command_read_settings(),
                      get_device_information()
        '''
        #Check if connection not open
        if not self.dev_open:
            #log closed connection
            self.report_error("Device not open, cannot get info.")
            return False

        #Try to get info
        try:
            #get serial number, power settings, device information
            self.serial_number = self._axis.get_serial_number()
            self.power_setting = self._axis.get_power_settings()
            self.device_information = self._axis.get_device_information()

            self.report_info("Device opened successfully.")
            self.report_info(f"Serial number: {self.serial_number}")
            self.report_info(f"Power setting: {self.power_setting}")
            self.report_info(f"Device information: {self.device_information}")
        except Exception as e: #pylint: disable=W0718
            #log error and return None
            self.report_error(f"Error getting device information: {e}")
        return None


    def home(self):
        '''
            Homes stage into "parked" positon
            -Will Home and stay at homed position.
            return: bool on successful home
            libximc:: command_homezero()
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot home stage.")
            return False

        try:
            #home stage,Check, and log status
            self._axis.command_homezero()
            self.report_info("home command sent successfully.")
            self.status()
            return True
        except Exception as e: #pylint: disable=W0718
            #log error
            self.report_error(f"Error homing stage: {e}")
            return False

    def set_pos(self, position:int, abs_move:bool=True): # pylint: disable=W0221
        '''
            Sets the current position of the stage to a specific value.
            - This does not move the stage, just sets the current position
            parameters: int:"position" to set current position to
            return: bool on successful or unsuccessful set position
            libximc:: set_position()
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot set position.")
            return False

        try:
            #set position, return true if succesful
            if abs_move:
                self.report_info("Setting position with absolute move.")
                self.move_abs(position)
                self.report_info(f"Position set to: {position}")
            else:
                self.report_info("Setting position relative to current position.")
                self.move_rel(position)
                self.report_info(f"Position moved by: {position}")
            return True
        except Exception as e: #pylint: disable=W0718
            #log error and return false
            self.report_error(f"Error setting position: {e}")
            return False

    def move_abs(self, position:int):
        '''
            Move the stage to a ABSOLUTE position. Send stage to any specific
                location within the device limits.
            - Check min_limit and max_limit for valid inputs
            parameters: min_limit < int:"position" < max_limit
            return: bool on successful or unsuccessful absolute move
            libximc:: command_move()
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot move stage.")
            return False

        try:
            #check limits/valid inputs
            if position < self.min_limit or position > self.max_limit:
                self.report_error(f"Position out of limits: {position}")
                return False
            self._axis.command_move(position, self._uPOSITION)
            return True
        except Exception as e: #pylint: disable=W0718
            #log error and return false
            self.report_error(f"Error moving stage: {e}")
            return False

    def move_rel(self, position:int):
        '''
            Move the stage to a RELATIVE position. Send stage to a position
                relative to its current position.
            - Check min_limit and max_limit for range of device
            parameters: min_limit < +- int for relative move < max_limit
            return: bool on successful or unsuccessful relative move
            libximc:: command_movr()
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot move stage.")
            return False

        try:
            #check limits/valid inputs
            #get current position, calculate new position, check limits
            current_position = self.get_pos()
            new_position = current_position + position
            if new_position < self.min_limit or new_position > self.max_limit:
                self.report_error(f"Position out of limits: {new_position}")
                return False
            #move relative
            self._axis.command_movr(position, self._uPOSITION)
            return True
        except Exception as e: #pylint: disable=W0718
            #log error and return false
            self.report_error(f"Error moving stage: {e}")
            return False

    def get_pos(self): # pylint: disable=W0221
        '''
            Gets Position of stage
            return: position in stage specific units
            libximc::
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot get position.")
            return False

        try:
            #get position
            pos = self._axis.get_position()
            self.report_info(f"Current position: {pos.Position}")
            return pos.Position
        except Exception as e: #pylint: disable=W0718
            #log error and return None
            self.report_error(f"Error getting position: {e}")
            return None

    def get_status(self):
        '''
            Gathers status and formats it in a usable and readable format.
                mostly for logging
            return: status string and variables nessesary
            libximc:: get_status()
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot get status.")
            return False

        try:
            #get status, parse results, return status in user friendly way
            self.status = self._axis.get_status()
            self.report_info(f"Position: {self.status.CurPosition}")
            self._homed_and_happy_bool = bool(self.status.Flags & self._state_flags.STATE_IS_HOMED |
                                                 self._state_flags.STATE_EEPROM_CONNECTED)
            return self.status
        except Exception as e: #pylint: disable=W0718
            #log error and return false
            self.report_error(f"Error getting status: {e}")
            return None

    def halt(self):
        '''
            IMMITATELY halts the stage, no matter the status or if moving, stage
                stops(for safety purposes)
            return: status of the stage(log and/or print hald command called)
            libximc:: command_stop()
        '''
        #Check if connection not open
        if not self.dev_open:
            self.report_error("Device not open, cannot halt stage.")
            return False

        try:
            #imidiate stop, check status, recurse
            self._axis.command_stop()
            status = self._axis.get_status()
            if status.MvCmdSts != self._move_cmd_flags.MVCMD_STOP:
                self.halt()  #Recursively call halt if not stopped

            #status.Moving
            self.report_info("Stage halted successfully.")
            return True
        except Exception as e: #pylint: disable=W0718
            #log error and return false
            self.report_error(f"Error halting stage: {e}")
            return False

    def is_homed(self) -> bool:
        """Check if the hardware motion device is homed."""
        self.get_status()
        return self._homed_and_happy_bool

    def get_limits(self) -> Union[Dict[str, Tuple[float, float]], None]:
        """
        Get the limits of the hardware motion device.

        Limits are the smallest and largest allowed positions for an axis.
        Axes are identified by a string and limits are a tuple.
        e.g.: {"1": (1, 6)} - for a filter wheel

        """
        #Set limits
        limits = self._axis.get_edges_settings()
        self.min_limit = limits.LeftBorder
        self.max_limit = limits.RightBorder
        self.report_info(f"Limits are: Min: {self.min_limit}, Max: {self.max_limit}")
        ret = {"1": (self.min_limit, self.max_limit)}
        return ret

    def close_loop(self) -> bool:
        """Close the loop for the hardware motion device."""
        return True

    def is_loop_closed(self) -> bool:
        """Check if the hardware motion loop is closed."""
        return True

    def _send_command(self, command: str) -> bool: # pylint: disable=W0221
        """Send a command to the hardware motion device."""
        raise NotImplementedError("Device does not use command/reply protocol.")

    def _read_reply(self) -> str:
        """Read a reply from the hardware motion device."""
        raise NotImplementedError("Device does not use command/reply protocol.")
