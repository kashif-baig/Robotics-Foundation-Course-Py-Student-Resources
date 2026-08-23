# Basic example that blinks LED with interval controlled by the
# potentiometer slider. A push button is used for turning the
# blinking on or off.

from app_config import *

try:
    # Connect to All-in-One kit
    all_in_one_kit.Connect()
    print("Press Esc to stop program.")

    # Variable to control the blinking
    blink_on = False

    while not escape_pressed():
        if blink_on:
            # Alternate the state of the LED
            if not led.IsOn:
                led.On()
            else:
                led.Off()
                
            # Pause for duration determined by slider
            time.sleep(1/(slider.Value/100 + 1))
        
        if button_pressed():
            blink_on = not blink_on
            led.Off()   
finally:
    all_in_one_kit.Close()

