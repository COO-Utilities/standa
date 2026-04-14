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
import time
from smc8 import SmcController

# Open connection examples  
dev = SmcController(log = False)
dev.connect(device_str = "192.168.31.123/9219", connection_type = "xinet")
# OR
dev.connect(device_str="/dev/ximc/00007DF6", connection_type = "serial")
time.sleep(.25)
# Initialize dev instance
dev.initialize() 

# checks status
status = dev.status() 

# Homes device
dev.home() 
time.sleep(5) #Give time for stage to move

# Query Position
pos = dev.get_pos() # Query Position

# Move to absolute position
dev.set_pos(position = 5) #positive ot negative
time.sleep(5)

# Move to position relative of its current pos
dev.set_pos(position = 10, abs_move = False) 
time.sleep(5)

# Perform absolute move
dev.move_abs(100)

# Perform relative move
dev.move_rel(-20)

print(dev.get_pos())   # Should be 80
dev.home()
time.sleep(5)
#Close connection
dev.disconnect()
```

## 🧪 Testing
Unit tests are located in `tests/` directory.

TODO: Make "Mock test" for PPC102 get_position and get_status which threw errors and was removed. 
    Assumed to be due to the byte and int convertion

To run tests from the project root based on what you need:
Software check:
```bash
pytest -m unit
```
Connection Test:
```bash
pytest -m default
```
Functionality Test:
```bash
pytest -m functional
```