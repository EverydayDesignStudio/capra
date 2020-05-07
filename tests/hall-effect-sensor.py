from time import sleep          # Allows us to call the sleep function to slow down our loop
import RPi.GPIO as GPIO         # Allows us to call our GPIO pins and names it just GPIO

GPIO.setmode(GPIO.BCM)           # Set's GPIO pins to BCM GPIO numbering
INPUT_PIN = 26                   # Sets our input pin
GPIO.setup(INPUT_PIN, GPIO.IN)   # Set our input pin to be an input

FLAG = False


# Create a function to run when the input is high
def inputLow(channel):
    print('0')


# Wait for the input to go low, run the function when it does
# GPIO.add_event_detect(INPUT_PIN, GPIO.FALLING, callback=inputLow, bouncetime=200)

# Start a loop that never ends
# while True:
#     print('3.3')
#     sleep(1)                    # Sleep for a full second before restarting our loop


# Start a loop that never ends
while True:
    # Physically read the pin now
    if (GPIO.input(INPUT_PIN)):
        print('true')
    else:
        print('false')

    sleep(1)                  # Sleep for a full second before restarting our loop
