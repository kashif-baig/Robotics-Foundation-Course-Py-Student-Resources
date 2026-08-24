# https://www.cohesivecomputing.co.uk/robotics/
#
# Basic example that blinks LED with interval controlled by the
# potentiometer slider and helper function.
#
# Make sure to correctly set the variable serial_port in the app_config.py file
# before running the program.

from app_config import *

# Helper function to calculate blink interval using slider position.
def blink_interval()->int:
    ''' Returns an interval value expressed in seconds using the slider position.'''
    return 1/(slider.Value/100 + 1)

try:
    # Connect to All-in-One kit
    all_in_one_kit.Connect()
    print("Press Esc to stop program.")

    while not escape_pressed():
        # Alternate the state of the LED
        if not led.IsOn:
            led.On()
        else:
            led.Off()
        
        # Pause for duration determined by slider
        time.sleep(blink_interval())
            
finally:
    all_in_one_kit.Close()

