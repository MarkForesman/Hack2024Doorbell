import json
from events import *
from picamera2 import Picamera2
import time
import subprocess
import uuid

# Initialize the camera
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
time.sleep(2)  # Allow the camera to warm up

class Scanner:
    def __init__(self, iothub, update_color):
        self.iothub = iothub
        self.update_color = update_color

    def button_1_press(self):
        print("Button 1 pressed")
        camera.capture_file('image1.jpg')
        try:
            result = subprocess.run(['python3', 'file_upload.py', 'image1.jpg'], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True)
            print("Subprocess completed successfully")
            print("Output:", result.stdout)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Subprocess failed with return code {e.returncode}: {e.stderr}")
        event=self.generate_button_event(1, "image.jpg")
        event_json=event.model_dump_json()
        self.iothub.send_message(event_json)
        self.update_color(1, 1, 0, 0) 

    def button_2_press(self):
        self.update_color(1, 1, 0, 0) 
        print("Button 2 pressed")
        # camera.capture_file('image2.jpg')

    def generate_button_event(self, button, file_name):
        return ButtonPressEvent(Button=button, DeviceType="LabelScanner", DeviceId=self.iothub.device_id, Metadata=file_name)     

    def message_received(self, message):
        print("Properties: ", message.custom_properties)
        msg = json.loads(message.data.decode("utf-8"))
        msgType = msg.get("Type")
        if  msgType == "PackageArrivedEvent":
             event = PackageArrivedEvent(**msg)
             print(f"Package arrived event received: {event}")
             self.update_color(1, 0, 1, 0)
        # else if "PackagePickerConfirmedEvent" in message:
        #     event = PackagePickerConfirmedEvent.model_validate_json(message)
        #     print(f"Package picker confirmed event received: {event}")
        #     #self.update_color(1, 0, 1, 0)
        else:
            print("Unknown message received")

