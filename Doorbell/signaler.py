import json
from events import *

class Signaler:
    light_reset = 500
    def __init__(self, client, update_color):
        print("signaler here")
        self.client = client
        self.update_color = update_color
        self.client.receive(self.message_received)

    def button_1_press(self):
        print("Button 1 pressed - Package picked up")
        event=self.generate_button_event(1)
        event_json=event.model_dump_json()
        print(event_json)
        self.client.send_message(event_json)
        # Orchestrator will send LED update

    def button_2_press(self):
        print("Button 2 pressed - Package picked up")
        event=self.generate_button_event(2)
        event_json=event.model_dump_json()
        print(event_json)
        self.client.send_message(event_json)
        # Orchestrator will send LED update

    def generate_button_event(self, button):
        return ButtonPressEvent(Button=button, DeviceType="Signaler", DeviceId=self.client.device_id, Metadata="")     

    def message_received(self, message):
        msg = json.loads(message.data.decode("utf-8"))
        print(f"Signaler received message: {msg}")
        msgType = msg.get("type")
        
        if msgType == "led_update":
            # Handle LED update from orchestrator
            cmd = msg.get("command", {})
            button = cmd.get("button", 1)
            red = cmd.get("red", 0)
            green = cmd.get("green", 0)
            blue = cmd.get("blue", 0)
            reset_after = cmd.get("reset_after", 0)
            
            if reset_after > 0:
                self.update_color(button, red, green, blue, reset_after)
            else:
                self.update_color(button, red, green, blue)
        else:
            print(f"Unknown message type: {msgType}")

