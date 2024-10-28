import json
from events import *
import multiprocessing
class Doorbell:
    light_reset = 60
    t1 = None
    b1 = False
    b2 = False
    def __init__(self, iothub, update_color, update_color_flash):
        print("Start doorbell init")
        self.iothub = iothub
        self.update_color = update_color
        self.update_color_flash = update_color_flash
        self.iothub.receive(self.message_received)
        #self.t1 = multiprocessing.Process(target=self.update_color_flash, args=())
        print("end doorbell init")

    def button_1_press(self):
        if self.b1:
                print("Doorbell 1 pressed")
                event=self.generate_button_event(1)
                event_json=event.model_dump_json()
                print(event_json)
                self.iothub.send_message(event_json)
                #self.update_color(1, 1, 0, 0, Doorbell.light_reset) 
                #self.update_color_flash(1, 1, 0, 0) 
                #self.t1.start()
                self.update_color_flash(True)
                print("thread started")
        else:
                self.b1 = True

    def button_2_press(self):
        if self.b2:
                print("Doorbell 2 pressed")
                event=self.generate_button_event(2)
                event_json=event.model_dump_json()
                print(event_json)
                self.iothub.send_message(event_json)
                #self.update_color(2, 1, 0, 0, Doorbell.light_reset)
                #self.update_color_flash(2, 1, 0, 0) 
                #self.t1.start()
                self.update_color_flash(True)
                print("thread started")
        else:
                self.b2 = True

    def generate_button_event(self, button):
        return ButtonPressEvent(Button=button, DeviceType="Doorbell", DeviceId=self.iothub.device_id, Metadata="")     

    def message_received(self, message):
        msg = json.loads(message.data.decode("utf-8"))
        print(msg)
        msgType = msg.get("Type")
        if  msgType == "PackagePickerConfirmedEvent":
             event = PackagePickerConfirmedEvent(**msg)
             self.update_color_flash(False)
        else:
            print(f"{msgType} is not supported by this device.")

