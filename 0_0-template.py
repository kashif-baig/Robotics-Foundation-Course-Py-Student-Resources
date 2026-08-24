# https://www.cohesivecomputing.co.uk/robotics/
#
# Python coding exercise template. Make sure to first copy this file to
# a new file and rename it before you start coding.
# 
# The new file name should be prefixed with the exercise heading number you are
# working on, e.g. "3_05 automatic night light.py", but without the quotes.
#
# Make sure to correctly set the variable serial_port in the app_config.py file
# before running the program.

from app_config import *

try:
    # Connect to All-in-One kit
    all_in_one_kit.Connect()
    print("Press Esc to stop program.")

    # Keep looping until Escape key pressed
    while not escape_pressed():
        pass
            
finally:
    all_in_one_kit.Close()
