# Import necessary libraries
from gpiozero import Button
from picamera2 import Picamera2
import time

# Initialize the camera
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
time.sleep(2)  # Allow the camera to warm up

# Define the button pins
buttonPin1 = 20
buttonPin2 = 21

# Create Button instances
button1 = Button(buttonPin1, pull_up=True, bounce_time=0.05)
button2 = Button(buttonPin2, pull_up=True, bounce_time=0.05)

# Define the button press functions
def button_1_pressed():
    print("Button 1 pressed")
    camera.capture_file('image1.jpg')

def button_2_pressed():
    print("Button 2 pressed")
    camera.capture_file('image2.jpg')

# Attach event handlers
button1.when_pressed = button_1_pressed
button2.when_pressed = button_2_pressed

# Keep the script running to listen for button presses
print("Script is running. Press buttons to capture images.")
while True:
    time.sleep(1)
