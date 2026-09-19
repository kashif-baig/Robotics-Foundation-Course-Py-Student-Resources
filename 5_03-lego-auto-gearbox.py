# https://www.cohesivecomputing.co.uk/robotics/
#
# Automated gearbox using LEGO, Arduino and Robo-Tx Education Edition API
#
# Deploy Robo-Tx firmware to Arduino (see link below). Make sure
# SELECTED_PROFILE is first set to PROFILE_ROBOT_MOTOR_SHIELD in file Settings.h
#
# https://github.com/kashif-baig/RoboTx_Firmware
#
# Robo-Tx API online help: https://help.cohesivecomputing.co.uk/Robo-Tx
#
# All examples are provided as is and at user's own risk.

import time
import datetime as dt
import threading
from pythonnet import load

load("coreclr")
import clr

# Use correct path for your OS platform.
clr.AddReference("./RoboTx/win-x64/Robo-Tx.Api")
from RoboTx.Api import RobotIO, Input
from RoboTx import *

# If connecting directly to an Arduino using USB, you can find the serial port using the Arduino IDE.
serial_port = "COM13"

state_neutral = 0
state_constant = 1
state_decelerating = 2
state_accelerating = 3

cmd_slow_down = 21
cmd_speed_up = 9

autoGearBox = RobotIO(serial_port)
try:
    autoGearBox.Connect()
    print("Press Enter to stop the program.")

    # Thread to detect Enter key
    detectEnter = threading.Thread(target=input)
    detectEnter.start()

    motor = autoGearBox.Motor1
    gear_lever = autoGearBox.Servo1
    
    # Configure servo range as 360 degrees.
    autoGearBox.ServoConfig.SetType(360, 500, 2500, gear_lever)

    # Set gear change latency in milliseconds.
    gear_change_latency = 0.030

    # Assume servo has speed of 0.18 sec/60 degrees.
    servo_ms_per_degree = 180 / 60000

    neutral_position = 178
    first_gear_position = 145
    second_gear_position = 210

    # Enable pulse measuring on pin A2.
    # The number of pulses per drive shaft revolution
    # depends on the wheel encoder pattern.
    timeout_ms = 1000
    trigger = 1
    autoGearBox.PulseCounter.Enable(timeout_ms, trigger)

    # Shift in to neutral.
    gear_lever.SetPosition(neutral_position - 15)
    time.sleep(0.2)
    gear_lever.SetPosition(neutral_position + 15)
    time.sleep(0.2)
    gear_lever.SetPosition(neutral_position)

    # Simulating motor under load. Lower values result in faster acceleration.
    motor_acceleration = 3

    servo_wait_time = servo_ms_per_degree * 35
    time.sleep(servo_wait_time + gear_change_latency)

    rpm = 0
    prev_rpm = -1

    is_in_first_gear = False
    state = state_neutral

    # Values obtained by trial and error when motor not under load.
    up_shift_rpm_threshold = 400
    up_shift_start_speed = 23
    down_shift_rpm_threshold = 370
    down_shift_start_speed = 45

    last_gear_shift_time = dt.datetime.now()
    min_gear_shift_interval = 2
    last_ir_cmd_code = -1

    # Keep looping until Enter key is pressed.
    while detectEnter.is_alive():
        ir_cmd = autoGearBox.Digital.GetIRCommand()

        if ir_cmd.Received:
            ir_state = "pressed" if ir_cmd.ButtonPressed else "released"
            print(f"IR Cmd: {ir_cmd.Code} {ir_state}")

            if ir_cmd.ButtonPressed:
                last_ir_cmd_code = ir_cmd.Code

            if ir_cmd.Code == cmd_slow_down:
                if ir_cmd.ButtonPressed:
                    if not is_in_first_gear and rpm > 0:
                        motor.Drive(up_shift_start_speed - 8)
                    elif rpm > 0:
                        motor.Drive(0)
                    state = state_decelerating
                elif ir_cmd.ButtonReleased and rpm > 0:
                    motor.StopAccelerating()
                    state = state_constant

            elif ir_cmd.Code == cmd_speed_up:
                if ir_cmd.ButtonPressed:
                    if rpm == 0:
                        motor.SetAcceleration(motor_acceleration)
                        gear_lever.SetPosition(first_gear_position)

                        is_in_first_gear = True
                        last_gear_shift_time = dt.datetime.now()
                    motor.Drive(95)
                    state = state_accelerating

                elif ir_cmd.ButtonReleased:
                    motor.StopAccelerating()
                    state = state_constant

        # Calculate drive shaft RPM
        rpm = (
            int((1000 * 30) / autoGearBox.PulseCounter.Period)
            if autoGearBox.PulseCounter.Period > 0
            else 0
        )
        if rpm != prev_rpm:
            prev_rpm = rpm
            print(f"RPM {rpm}")
        if rpm == 0:
            if state != state_neutral and last_ir_cmd_code == cmd_slow_down:
                state = state_neutral
                gear_lever.SetPosition(neutral_position + 10)
                time.sleep(0.2)
                gear_lever.SetPosition(neutral_position)
                motor.Drive(0)

        if (
            rpm > up_shift_rpm_threshold
            and is_in_first_gear
            and (dt.datetime.now() - last_gear_shift_time).total_seconds() > min_gear_shift_interval
        ):
            motor.StopAccelerating()
            print("Gear change up")
            motor.SetAcceleration(motor_acceleration)

            gear_lever.SetPosition(neutral_position)
            time.sleep(servo_wait_time)
            motor.DriveNoAccel(up_shift_start_speed)

            gear_lever.SetPosition(second_gear_position)
            time.sleep(servo_wait_time + gear_change_latency)

            if state == state_accelerating:
                motor.Drive(95)

            is_in_first_gear = False
            last_gear_shift_time = dt.datetime.now()
        elif (
            rpm != 0
            and rpm < down_shift_rpm_threshold
            and not is_in_first_gear
            and (dt.datetime.now() - last_gear_shift_time).total_seconds() > min_gear_shift_interval
        ):
            motor.StopAccelerating()
            print("Gear change down")
            motor.SetAcceleration(motor_acceleration)

            gear_lever.SetPosition(neutral_position)
            time.sleep(servo_wait_time)
            motor.DriveNoAccel(down_shift_start_speed)

            gear_lever.SetPosition(first_gear_position)
            time.sleep(servo_wait_time + gear_change_latency)

            if state == state_decelerating:
                motor.Drive(0)
            is_in_first_gear = True
            last_gear_shift_time = dt.datetime.now()
        time.sleep(0.01)
finally:
    autoGearBox.Close()

