import json
from events import *
import multiprocessing
class Doorbell:
    light_reset = 60
    t1 = None
    b1 = False
    b2 = False
    def __init__(self, client, update_color, update_color_flash):
        print("Start doorbell init")
        self.client = client
        self.update_color = update_color
        self.update_color_flash = update_color_flash
        self.client.receive(self.message_received)
        #self.t1 = multiprocessing.Process(target=self.update_color_flash, args=())
        print("end doorbell init")

    def button_1_press(self):
        if self.b1:
                print("Doorbell 1 pressed")
                event=self.generate_button_event(1)
                event_json=event.model_dump_json()
                print(event_json)
                self.client.send_message(event_json)
                # Orchestrator will send LED update
                print("Button press sent to orchestrator")
        else:
                self.b1 = True

    def button_2_press(self):
        if self.b2:
                print("Doorbell 2 pressed")
                event=self.generate_button_event(2)
                event_json=event.model_dump_json()
                print(event_json)
                self.client.send_message(event_json)
                # Orchestrator will send LED update
                print("Button press sent to orchestrator")
        else:
                self.b2 = True

    def generate_button_event(self, button):
        return ButtonPressEvent(Button=button, DeviceType="Doorbell", DeviceId=self.client.device_id, Metadata="")     

    def message_received(self, message):
        msg = json.loads(message.data.decode("utf-8"))
        print(f"Doorbell received message: {msg}")
        msgType = msg.get("type")
        
        if msgType == "led_update":
            # Handle LED update from orchestrator
            cmd = msg.get("command", {})
            button = cmd.get("button", 1)
            red = cmd.get("red", 0)
            green = cmd.get("green", 0)
            blue = cmd.get("blue", 0)
            flash = cmd.get("flash", False)
            reset_after = cmd.get("reset_after", 0)
            
            if flash:
                self.update_color_flash(True)
            else:
                self.update_color_flash(False)
                if reset_after > 0:
                    self.update_color(button, red, green, blue, reset_after)
                else:
                    self.update_color(button, red, green, blue)
        else:
            print(f"{msgType} is not supported by this device.")

