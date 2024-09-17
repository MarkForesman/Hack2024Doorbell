from azure.iot.device import IoTHubDeviceClient, Message
import time

# Define connection string for your device
connection_string = ''

# Create an IoT Hub client instance
client = IoTHubDeviceClient.create_from_connection_string(connection_string)

# Define a function to handle incoming messages
def message_handler(message):
    print("Received message:")
    print("Data: ", message.data.decode("utf-8"))
    print("Properties: ", message.custom_properties)

# Set the message handler on the client
client.on_message_received = message_handler

# Define a function to handle direct method calls (optional)
def method_handler(method_request):
    print("Received direct method:")
    print("Method Name: ", method_request.name)
    print("Payload: ", method_request.payload)

    # Respond to the method call
    client.send_method_response(
        method_request.response(
            status=200,
            payload={"result": "success"}
        )
    )

# Set the method handler on the client (optional)
client.on_method_request_received = method_handler

# Main loop
if __name__ == "__main__":
    try:
        print("Listening for messages and method calls...")
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        print("Stopping receiver...")
    finally:
        # Gracefully close the client
        client.shutdown()
