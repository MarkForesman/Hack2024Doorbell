#libraries
from time import sleep
from picamera2 import Picamera2

print('start')
camera = Picamera2()
#init camera
camera.configure(camera.create_still_configuration())
#start camera preview
camera.start()
sleep(2)
camera.capture_file('./image1.jpg')
while True:
	print('working')
	sleep(10)

