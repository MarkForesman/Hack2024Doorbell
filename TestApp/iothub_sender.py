#pip install azure-iot-device

from azure.iot.device import IoTHubDeviceClient, Message
import time

# Define connection string for your device
connection_string = 'HostName=DoorbellHub.azure-devices.net;DeviceId=106;SharedAccessKey=l0wcHhBsiW0+6ksma2NDJ891L6yGwv+ULAIoTEmILfk='

# Create an IoT Hub client instance
client = IoTHubDeviceClient.create_from_connection_string(connection_string)

def send_message(client):
    # Create a message to send
    message = Message("Hello, IoT Hub!")
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    
    # Send the message
    client.send_message(message)
    print("Message sent!")

# Main loop
if __name__ == "__main__":
    try:
        while True:
            send_message(client)
            time.sleep(10)  # Wait for 10 seconds before sending the next message
    except KeyboardInterrupt:
        print("Sending stopped by user.")
    finally:
        # Gracefully close the client
        client.shutdown()
