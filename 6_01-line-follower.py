# https://www.cohesivecomputing.co.uk/robotics/
#
# Line following vehicle using Cytron Maker-line line sensor, Arduino and Robo-Tx API.
#
# Deploy Robo-Tx firmware to Arduino (see link below). Make sure
# SELECTED_PROFILE is first set to PROFILE_UNO_MOTOR_PLUS in file Settings.h
#
# https://github.com/kashif-baig/RoboTx_Firmware
#
# Robo-Tx API online help: https://help.cohesivecomputing.co.uk/Robo-Tx
#
# All examples are provided as is and at user's own risk.
from vehicle_config import *

try:
    # Connect vehicle
    vehicle.Connect()
    print("Press Esc or Ctrl C to stop program.")

    # Set the default acceleration/deceleration for the motors.
    motor_left.SetAcceleration(0.5)
    motor_right.SetAcceleration(0.5)

    # ---------------------------------------------------------
    # PID line-following vehicle
    # ---------------------------------------------------------

    # Using the analog output of a Cytron Maker-line line sensor.
    # The line sensor is centred when it reports 511.
    LINE_CENTRE = 511

    # Motor speed when the vehicle is travelling straight.
    BASE_SPEED = 55

    # PID constants.
    # These values may need adjusting for your vehicle.
    Kp = 0.08
    Ki = 0.0001  
    Kd = 0.15

    # Keep track of the previous error and accumulated error.
    previous_error = 0
    total_error = 0

    # Keep looping until Escape key pressed
    while not escape_pressed():

        # Read the line sensor.
        sensor_value = line_sensor.Value

        # If the sensor cannot see the line, stop the vehicle gradually
        # using the default acceleration. Gradually stopping the vehicle
        # gives it time to move back onto the line if it has just lost it.
        if sensor_value < 90 or sensor_value > 990:
            motor_left.Drive(0)
            motor_right.Drive(0)

        else:
            # Calculate how far the vehicle is from the centre
            # of the line.
            error = sensor_value - LINE_CENTRE

            # P - Proportional
            # A larger error produces a larger correction.
            proportional = Kp * error

            # I - Integral
            # Add the current error to the accumulated error.
            total_error = total_error + error
            integral = Ki * total_error

            # D - Derivative
            # Calculate how quickly the error is changing.
            change_in_error = error - previous_error
            derivative = Kd * change_in_error

            # Add the three PID terms together.
            correction = proportional + integral + derivative

            # Remember the error for the next loop.
            previous_error = error

            # Apply the correction to the two motors.
            # Change signs of the correction values to steer in
            # the opposite direction.
            left_speed = clamp(BASE_SPEED - correction, -100, 100)
            right_speed = clamp(BASE_SPEED + correction, -100, 100)

            # Drive the motors without acceleration.
            motor_left.DriveNoAccel(left_speed)
            motor_right.DriveNoAccel(right_speed)

finally:
    vehicle.Close()
