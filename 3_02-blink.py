# Basic example that blinks LED with fixed interval of 1 second.
#
# Make sure to correctly set the variable serial_port in the app_config.py file
# before running the program.

from app_config import *

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
        
        # Pause for 1 second
        time.sleep(1)
            
finally:
    all_in_one_kit.Close()

