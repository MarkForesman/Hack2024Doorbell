from azure.iot.device import IoTHubDeviceClient, Message
import time

import os
from dotenv import load_dotenv
load_dotenv(override=True)

# Define connection string for your device
connection_string = os.getenv("IOT_CONNECTION_STRING")

class IoTHub:
    def __init__(self):
       self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
       key_value_pairs = connection_string.split(';')
       for pair in key_value_pairs:
        if pair.startswith("DeviceId="):
            self.device_id = pair.split('=')[1]
            break

    def send_message(self, str_message):
        message = Message(str_message)
        message.content_encoding = "utf-8"
        message.content_type = "application/json"
        self.client.send_message(message)

    def receive(self, message_received_callback):
       self.client.on_message_received = message_received_callback
    
    def disconnect(self):
        self.client.shutdown()