#libraries
import RPi.GPIO as GPIO
import threading
from time import sleep
#from gpiozero import Button
import os
from dotenv import load_dotenv
from iothub import IoTHub
load_dotenv(override=True)

print("start")

# Define connection string for your device
connection_string = os.getenv("IOT_CONNECTION_STRING")
device_mode = os.getenv("DEVICE_MODE")
#from picamera2 import Picamera2

#set red,green and blue pins
redPin1 = 2
greenPin1 = 4
bluePin1 = 3
buttonPin1 = 21

redPin2 = 5
greenPin2 = 13
bluePin2 = 6
buttonPin2 = 20

#button1 = Button(buttonPin1, pull_up = True, bounce_time = 0.05)
#button2 = Button(buttonPin2, pull_up = True, bounce_time = 0.05)

#camera = Picamera2()

# def button_1_pressed():
#     print("button1 pressed")
#     camera.capture_file('/home/pi/Hack2024/image1.jpg')
#     updateColor(1, 1, 0, 0) 

# def button_2_pressed():
#     print("button_2 pressed")
#     camera.capture_file('/home/pi/Hack2024/image2.jpg')
#     updateColor(2, 1, 0, 0) 

# def button_1_released():
#     print("button_1 released")

# def button_2_released():
#     print("button_2 released")

def init_GPIO():
    #disable warnings (optional)
    GPIO.setwarnings(False)
    #Select GPIO Mode
    GPIO.setmode(GPIO.BCM)

    #set pins as outputs
    GPIO.setup(redPin1,GPIO.OUT)
    GPIO.setup(greenPin1,GPIO.OUT)
    GPIO.setup(bluePin1,GPIO.OUT)

    GPIO.setup(redPin2,GPIO.OUT)
    GPIO.setup(greenPin2,GPIO.OUT)
    GPIO.setup(bluePin2,GPIO.OUT)
    
    GPIO.setup(buttonPin1, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(buttonPin2, GPIO.IN, GPIO.PUD_UP)

    for i in range(5):
        updateColor(1, 1, 0, 1)
        updateColor(2, 1, 0, 1)
        sleep(.05)
        updateColor(1, 0, 0, 0)
        updateColor(2, 0, 0, 0)
        sleep(.05)


#Attach event handlers for switch press and release


    # button1.when_pressed = button_1_pressed
    # button1.when_released = button_1_released

    # button2.when_pressed = button_2_pressed
    # button2.when_released = button_2_released

# def init_camera():
#     #init camera
#     camera.configure(camera.create_still_configuration())
#     #start camera preview
#     camera.start()
#     sleep(2)


def updateColor(button_num, red, green, blue, reset_after=0):
    if button_num ==1 :
        GPIO.output(redPin1,red)
        GPIO.output(greenPin1,green)
        GPIO.output(bluePin1,blue)
    else:
        GPIO.output(redPin2,red)
        GPIO.output(greenPin2,green)
        GPIO.output(bluePin2,blue)
    if reset_after > 0:
        threading.Timer(reset_after, updateColor, [button_num, 0, 0, 0]).start()



init_GPIO()
device = None
iothub = IoTHub()
if device_mode == "Signaler":
    from signaler import Signaler
    device = Signaler(iothub, updateColor)
elif device_mode == "Doorbell":
    from doorbell import Doorbell
    device = Doorbell(iothub, updateColor)
elif device_mode == "LabelScanner":
    from label_scanner import Scanner
    device = Scanner(iothub, updateColor)


#button1.when_pressed = device.button_1_press
#button2.when_pressed = device.button_2_press


print(device_mode)

# Create a timer that runs `my_function` after 5 seconds

def button_1_pressed():
    print("button1 pressed_")
    device.button_1_press

def button_2_pressed():
    print("button_2 pressed_")
    device.button_2_press

def button_1_released():
    print("button_1 released_")

def button_2_released():
    print("button_2 released_")


lastbuttonstate1 = False
lastbuttonstate2 = False

print("running")

while True:
    buttonstate1 = GPIO.input(buttonPin1)
    buttonstate2 = GPIO.input(buttonPin2)
    if buttonstate1 != lastbuttonstate1:
        if buttonstate1:
            button_1_pressed()
        else:
            button_1_released()

    lastbuttonstate1 = buttonstate1
    if buttonstate2 != lastbuttonstate2:
        if buttonstate2:
            button_2_pressed()
        else:
            button_2_released()

    lastbuttonstate2 = buttonstate2
    sleep(.01)


'''
def turnOff():
    GPIO.output(redPin,GPIO.HIGH)
    GPIO.output(greenPin,GPIO.HIGH)
    GPIO.output(bluePin,GPIO.HIGH)
    
def white():
    GPIO.output(redPin,GPIO.LOW)
    GPIO.output(greenPin,GPIO.LOW)
    GPIO.output(bluePin,GPIO.LOW)
    
def red():
    GPIO.output(redPin,GPIO.LOW)
    GPIO.output(greenPin,GPIO.HIGH)
    GPIO.output(bluePin,GPIO.HIGH)

def green():
    GPIO.output(redPin,GPIO.HIGH)
    GPIO.output(greenPin,GPIO.LOW)
    GPIO.output(bluePin,GPIO.HIGH)
    
def blue():
    GPIO.output(redPin,GPIO.HIGH)
    GPIO.output(greenPin,GPIO.HIGH)
    GPIO.output(bluePin,GPIO.LOW)
    
def yellow():
    GPIO.output(redPin,GPIO.LOW)
    GPIO.output(greenPin,GPIO.LOW)
    GPIO.output(bluePin,GPIO.HIGH)
    
def purple():
    GPIO.output(redPin,GPIO.LOW)
    GPIO.output(greenPin,GPIO.HIGH)
    GPIO.output(bluePin,GPIO.LOW)
    
def lightBlue():
    GPIO.output(redPin,GPIO.HIGH)
    GPIO.output(greenPin,GPIO.LOW)
    GPIO.output(bluePin,GPIO.LOW)
'''
