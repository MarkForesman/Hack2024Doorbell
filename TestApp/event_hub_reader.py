from azure.eventhub import EventHubConsumerClient
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# Replace these with your actual Event Hub details
connection_str = os.getenv("CONNECTION_STRING")

consumer_group = '$Default'  # Replace with your consumer group if different
eventhub_name = 'doorbellhub'  # The name of your Event Hub

def on_event(partition_context, event):
    # Called when an event is received
    print("Received event from partition: {}.".format(partition_context.partition_id))
    print("Event data: {}".format(event.body_as_str()))
    # You can also use event.metadata for more information if needed

def on_error(partition_context, error):
    # Called when an error occurs
    print("Error occurred: {}".format(error))

def on_partition_initialize(partition_context):
    # Called when a partition is initialized
    print("Partition initialized: {}".format(partition_context.partition_id))

def on_partition_close(partition_context, reason):
    # Called when a partition is closed
    print("Partition closed: {}. Reason: {}".format(partition_context.partition_id, reason))

# Create a consumer client for the Event Hub
client = EventHubConsumerClient.from_connection_string(
    connection_str,
    consumer_group=consumer_group
)

try:
    # Start receiving messages
    with client:
        client.receive(
            on_event=on_event,
            on_error=on_error,
            on_partition_initialize=on_partition_initialize,
            on_partition_close=on_partition_close,
            consumer_group=consumer_group,
            starting_position="@latest",  # Change to "@earliest" if you want to read from the beginning
            eventhub_name=eventhub_name
        )
except KeyboardInterrupt:
    print("Receiving has been stopped.")
finally:
    # Close the client
    client.close()
