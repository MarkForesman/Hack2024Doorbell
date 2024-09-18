import json
from events import *
class Signaler:
    def __init__(self, iothub, update_color):
        self.iothub = iothub
        self.update_color = update_color
        self.iothub.receive(self.message_received)

    def button_1_press(self):
        print("Button 1 pressed")
        #change from doorbell or siganler later
        event=self.generate_button_event(1)
        event_json=event.model_dump_json()
        print(event_json)
        self.iothub.send_message(event_json)
        self.update_color(1, 1, 0, 0) 

    def button_2_press(self):
        print("Button 2 pressed")
        event=self.generate_button_event(2)
        event_json=event.model_dump_json()
        print(event_json)
        self.update_color(2, 1, 0, 0) 

    def generate_button_event(self, button):
        return ButtonPressEvent(Button=button, DeviceType="Doorbell", DeviceId=self.iothub.device_id, Metadata="")     

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

