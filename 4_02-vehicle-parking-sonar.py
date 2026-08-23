# Sonar ranging application that uses sonar to measure distance (max 250 cm) of object
# from sensor. Sound is emmited from the buzzer with an interval that corresponds to
# the distance.

from app_config import *

try:
    all_in_one_kit.Connect()
    print("Press Esc to stop program.")

    # Start beeper repeating indefinitely: 50ms beep, 950ms interval.
    beeper.Repeat(50, 950)
   
    while not escape_pressed():

        if not sonar.DistanceAcquired:
            # Emit ping from sonar module.
            sonar.Ping()
        else:
            # Retrieve the measured distance in centimeters.
            distance_cm = sonar.GetDistance()

            # Calculate beep interval (in milliseconds) to correspond to distance.
            beep_interval = (distance_cm * 10)

            # If measured distance is less than 3 cm, set beep interval to 0 to emit
            # continuous sound.
            if distance_cm < 3:
                beep_interval = 0

            # Set beeper interval.
            beeper.SetOffPeriod(beep_interval)

            # Show the distance on the display, right justified.
            display.PrintAt(10, 0, f"{distance_cm} cm".rjust(6))

        time.sleep(0.1)
finally:
    all_in_one_kit.Close()

