# https://www.cohesivecomputing.co.uk/robotics/
#
# Requires a version of Python no later than 3.14, and dot net version no earlier than 8.0.
# Ensure pythonnet has been installed in the Python virtual environment.

import threading
import time,math
from datetime import datetime,timedelta

from pythonnet import load
load("coreclr")
import clr

# Use correct path for your OS platform.
clr.AddReference("./RoboTx/linux-arm64/Robo-Tx.Api")
from RoboTx.Api import RobotIO, Input, AnalogConverter, IrCommandConverter
from RoboTx import *

# If connecting to an Arduino using USB, use Device Manager (Windows OS) to identify the COM port.
serial_port = "/dev/ttyUSB0"

vehicle = RobotIO(serial_port)
'''Manages interaction with the All in One Kit.'''

# Assign sensors to variables
line_sensor = vehicle.Analog.A6
'''
Value represents position of the line. 511 represents the line is centered,
102 represents the line is far left, 902 represents the line is far right.
'''

distance_sensor = vehicle.Analog.A7
'''
Assuming GP2Y0A60SZLF IR distance sensor.
Value corresponds to distance from an object (10 to 150 cm).
'''

# Assign actuators to variable
motor_left = vehicle.Motor1
'''A DC motor on left side of vehicle.'''
motor_right = vehicle.Motor2
'''A DC motor on right side of vehicle.'''

proximity_left = vehicle.Digital.IN1
proximity_right = vehicle.Digital.IN0


def clamp(value, minimum, maximum):
    '''
    Clamps a value between a minimum and maximum.
    '''
    return max(minimum, min(value, maximum))

def convert_to_centimeters(analog_value: float) -> float:
    '''
    Converts analog reading of GP2Y0A60SZLF distance sensor to distance in centimeters.
    Returns -1 if the analog value is outside the valid range for this sensor.
    '''
    if (analog_value >= 93 and analog_value <= 786):
        return 32324 * analog_value**-1.229
    return -1

# Helper to detect an Escape key press (Windows implementation)
def escape_pressed() -> bool:
    """
    Returns True if the Escape key was pressed.
    Works on Windows using msvcrt. On other platforms it always returns False.
    """
    try:
        time.sleep(0.02)
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # msvcrt returns b'\x1b' for Escape
            return key == b'\x1b'
    except ImportError:
        # Platform does not support msvcrt (e.g., Linux/macOS)
        # Implementations using termios/select could be added here.
        pass
    return not vehicle.ConnectionState.IsConnected