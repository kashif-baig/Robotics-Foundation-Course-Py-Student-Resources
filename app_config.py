# Install a version of Python no later than 3.14, and dot net version no earlier than 8.0.
# Ensure pythonnet is installed by issuing the following on a command line of the
# selected Python environment:
# pip install pythonnet

import threading
import time,math
from datetime import datetime,timedelta

from pythonnet import load
load("coreclr")
import clr

# Use correct path for your OS platform.
clr.AddReference("./RoboTx/win-x64/Robo-Tx.Api")
from RoboTx.Api import RobotIO, Input, AnalogConverter, IrCommandConverter
from RoboTx import *

# If connecting to an Arduino using USB, use Device Manager (Windows OS) to identify the COM port.
# For Linux, try the default port "/dev/ttyACM0".
serial_port = "COM8"

all_in_one_kit = RobotIO(serial_port)
'''Manages interaction with the All in One Kit.'''

# Assign sensors to variables
slider = all_in_one_kit.Analog.A0
'''Value represents position of the slider (0 to 1023).'''
light_meter = all_in_one_kit.LightMeter
'''Reports ambient LUX value (0 to 50000). 0 indicates total darkness, 400 approximates good ambient indoor lighting.'''
colour_sensor = all_in_one_kit.ColourSensor
dht_sensor = all_in_one_kit.DHTSensor
rain_sensor = all_in_one_kit.Analog.A6
'''Value corresponds to amount of moisture (0 to 1023). 0 indicates no moisture, 1023 indicates maximum moisture.'''
temp_sensor = all_in_one_kit.Analog.A6
'''Value corresponds to ambient temperature (0 to 1023)'''
motion_detected = all_in_one_kit.Digital.IN1
'''Value is true if motion was detected, false otherwise.'''
pulse_counter = all_in_one_kit.PulseCounter
sonar = all_in_one_kit.Sonar
sound_sensor = all_in_one_kit.Analog.A1
'''Value corresponse to sound loudness (0 to 1023). 0 indicates silence, 1023 maximum loudness.'''

# Assign actuator to variable
buzzer = all_in_one_kit.Trigger
'''Sound beeps as a single pulse, or as a pattern.'''
beeper = all_in_one_kit.Trigger
'''Sound beeps as a single pulse, or as a pattern.'''
display = all_in_one_kit.Display
'''16 x 2 Liquid Crystal Display.'''
led = all_in_one_kit.Switch2
'''Light Emmitting Diode (LED).'''
light = led
'''Light Emmitting Diode (LED).'''
relay = all_in_one_kit.Switch1
'''An electrically controlled switch for turning high current devices on or off.'''
servo = all_in_one_kit.Servo1
'''A 180 degree servo motor.'''
fan = all_in_one_kit.Motor2
'''A DC motor that drives a fan.'''
mpu_sensor = all_in_one_kit.MPUSensor
'''A motion processing unit that reports accelerometer and gyro values.'''

def button_pressed()->bool:
    '''Returns True if the button was pressed, false otherwise.'''
    global all_in_one_kit
    return all_in_one_kit.Digital.GetInputEvent() == Input.BUTTON_1_PRESSED

def button_held()->bool:
    '''Returns True if the button was held, false otherwise.'''
    global all_in_one_kit
    input_event = all_in_one_kit.Digital.GetInputEvent()
    return input_event == Input.BUTTON_1_SUSTAINED or input_event == Input.BUTTON_1_PRESSED

def get_ir_code()->int:
    '''Gets the IR command button code if pressed, -1 otherwise.'''
    ir_cmd = all_in_one_kit.Digital.GetIRCommand()
    return ir_cmd.Code if ir_cmd.ButtonPressed else -1

_filtered_temp =0.0

def get_temperature()->float:
    '''Returns the temperature from an analog sensor with filtering applied.'''
    global _filtered_temp
    temp_value = (temp_sensor.Value * 500)/1023
    _filtered_temp = _filtered_temp * 0.8 + temp_value * 0.2
    return _filtered_temp

# Define the reference colours and their HSL ranges.
# Each entry is a tuple:
# (colour_name, hue_min, hue_max, sat_min, sat_max, light_min, light_max)
rubiks_colours = [
    ("white",   150, 155, 17, 21, 32, 33),
    ("red",       1,   7, 21, 30, 34, 37),
    ("orange",   53,  56, 35, 46, 27, 31),
    ("yellow",   77,  81, 37, 45, 30, 33),
    ("green",   135, 142, 24, 45, 32, 36),
    ("blue",    197, 206, 27, 59, 30, 32),
]


def detected_colour ()->str:
    '''Gets the name of the colour detected by the colour sensor. Currently restricted to
    Rubik's cube colours. Returns None if no colour detected.'''
    global rubiks_colours
    
    # Obtain the raw HSL values from the colour sensor.
    col = colour_sensor.GetHSL()

    # Find which reference colour matches the detected HSL values.
    for (
        colour_name,
        hue_min, hue_max,
        sat_min, sat_max,
        light_min, light_max,
    ) in rubiks_colours:
        if (
            hue_min <= col.Hue <= hue_max
            and sat_min <= col.Saturation <= sat_max
            and light_min <= col.Lightness <= light_max
        ):
            return colour_name
    return None


rad_to_deg = 180 / 3.14159

def incline_angle ()->float:
    '''Reports the incline angle measured by the mpu_sensor.'''
    return math.atan(mpu_sensor.Accel.X / mpu_sensor.Accel.Z) * rad_to_deg


# Helper function to map one range of values to another.
def map_range(value, from_low, from_high, to_low, to_high):
    '''
    Maps one range of values to another.
    '''
    if value < from_low:
        value = from_low
    elif value > from_high:
        value = from_high

    return int(((value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low) + 0.5)

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
    return not all_in_one_kit.ConnectionState.IsConnected