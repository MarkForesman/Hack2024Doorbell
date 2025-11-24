#libraries
import RPi.GPIO as GPIO
import threading
from time import sleep
#from gpiozero import Button
import multiprocessing
import os
from dotenv import load_dotenv
load_dotenv(override=True)

print("start")

# Define device configuration
device_id = os.getenv("DEVICE_ID")
device_mode = os.getenv("DEVICE_MODE")
#from picamera2 import Picamera2
print(device_mode)
#set red,green and blue pins
redPin1 = 2
greenPin1 = 4
bluePin1 = 3
buttonPin1 = 21

redPin2 = 5
greenPin2 = 13
bluePin2 = 6
buttonPin2 = 20

micPin = 23

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
    GPIO.setup(micPin, GPIO.IN, GPIO.PUD_UP)

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
    flash = False
    print("update color")
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

t1 = None
on = False
def updateColorFlash(_on):
    global on
    on = _on
    print(on)
    if on:
        t1 = multiprocessing.Process(target=blink(), args=())
        t1.start()
    else:
        t1 = None
        updateColor(1,0,1,0,60)
        updateColor(2,0,1,0,60)
   
def blink():
    global on
    print(on)
    while on:
        GPIO.output(redPin1,1)
        GPIO.output(greenPin1,0)
        GPIO.output(bluePin1,0)

        GPIO.output(redPin2,1)
        GPIO.output(greenPin2,0)
        GPIO.output(bluePin2,0)
        sleep(1)

        GPIO.output(redPin1,0)
        GPIO.output(greenPin1,0)
        GPIO.output(bluePin1,0)

        GPIO.output(redPin2,0)
        GPIO.output(greenPin2,0)
        GPIO.output(bluePin2,0)
        sleep(1)
        print("blink")
    print("end of blink")

init_GPIO()
device = None
client = None
try:
    from tcp_client import TcpClient
    client = TcpClient()
except Exception as e:
    print(f"Failed to initialize TCP client: {e}")
    print("Exiting...")
    import sys
    sys.exit(1)

if device_mode == "Signaler":
    from signaler import Signaler
    device = Signaler(client, updateColor)
elif device_mode == "Doorbell":
    from doorbell import Doorbell
    device = Doorbell(client, updateColor,updateColorFlash)
elif device_mode == "LabelScanner":
    from label_scanner import Scanner
    device = Scanner(client, updateColor)


#button1.when_pressed = device.button_1_press
#button2.when_pressed = device.button_2_press


print(device_mode)

# Create a timer that runs `my_function` after 5 seconds

def button_1_pressed():
    device.button_1_press()
    print("button_1 pressed_")
    

def button_2_pressed():    
    device.button_2_press()
    print("button_2 pressed_")


def button_1_released():
    print("button_1 released_")

def button_2_released():
    print("button_2 released_")


lastbuttonstate1 = True
lastbuttonstate2 = True
lastmicState = True
print("running newest")
hostname = "google.com" #example
response = os.system(f"ping -n -c 1 {hostname}")
print(response)

if response == 0:
    print(f"{hostname} is up!")
else:
    print(f"{hostname} is down!")
    updateColor(1, 100, 100, 100,3)
    updateColor(2, 100, 100, 100,3)

count = 0
while True:
    buttonstate1 = GPIO.input(buttonPin1)
    buttonstate2 = GPIO.input(buttonPin2)
    micState = GPIO.input(micPin)
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
    
    if micState != lastmicState:
        if micState:
            device.button_1_press()
            sleep(1)
        else:
            print("sound off")
    lastmicState = micState
    lastbuttonstate2 = buttonstate2
    sleep(.01)
    count = count + 1
    if count > 1000:
        hostname = "google.com" #example
        response = os.system(f"ping -n -c 1 {hostname}")
        #print(response)

        if response == 0:
            print(f"{hostname} is up!")
        else:
            print(f"{hostname} is down!")
            updateColor(1, 50, 50, 50,9)
            updateColor(2, 50, 50, 50,9)
        count=0


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
