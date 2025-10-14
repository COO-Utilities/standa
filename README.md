# Standa Controllers

Low-level Python or simplified wrapper modules to send commands to Standa controllers.

## Currently Supported Models
- 8SMC5 - smc8.py

## Features
- Connect to Standa Controllers
- Query state and parameters
- Move individual axes to absolute or relative positions

## Usage

### smc8.py Example
```python
    from util.smc8 import SMC

    # Open connection    
    dev = SMC(device_uri="",log = True)
    dev.open_connection()
    time.sleep(.25)
    #Populates dev with device info
    dev.get_info() 

    # checks status
    status = dev.status() 

    # Homes device
    dev.home() 
    time.sleep(5) #Give time for stage to move

    # Query Position
    pos = dev.get_position() # Query Position

    # Move Relative to its current position
    dev.move_rel(position = 5) #positive ot negative
    time.sleep(5)

    # Move to absolute position
    dev.move_abs(position = 10) 
    time.sleep(5)

    pos = dev.get_position()
    dev.home()
    time.sleep(5)
    #Close connection
    dev.close_connection()
```

## 🧪 Testing
Unit tests are located in `tests/` directory.

To run all tests from the project root:

```bash
python -m pytest -m unit/integration/default
```