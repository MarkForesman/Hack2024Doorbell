from azure.eventhub import EventHubConsumerClient

# Define connection parameters
connection_str = 'Endpoint=sb://iothub-ns-doorbellhu-62180401-c50c8fa2da.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=EEc8xYmwo/uXLABv2NKot0qOrWg5d/J7hAIoTPjoWXg=;EntityPath=doorbellhub'
eventhub_name = 'doorbell'
consumer_group = '$Default'  # Default consumer group; replace if needed

# Define a callback function to process incoming events
def on_event(partition_context, event):
    print("Received event:")
    print("Partition: ", partition_context.partition_id)
    print("Event Data: ", event.body_as_str())
    print("Sequence Number: ", event.sequence_number)
    print("Offset: ", event.offset)
    print("Enqueued Time: ", event.enqueued_time)

# Define a callback function for error handling
def on_error(partition_context, error):
    print("Error occurred: ", error)

# Create a consumer client
client = EventHubConsumerClient.from_connection_string(
    connection_str,
    consumer_group,
    eventhub_name=eventhub_name
)

# Start receiving messages
with client:
    # Create a receiver for all partitions
    try:
        # Start receiving messages from the Event Hub
        # This will call `on_event` whenever a message is received
        client.receive(
            on_event=on_event,
            on_error=on_error,
            consumer_group=consumer_group,
            starting_position="-1"  # Start receiving from the beginning of the partition
        )

        # Keep the script running to keep receiving messages
        print("Receiving messages. Press Ctrl+C to exit.")
        client._running_event.wait()  # Block until Ctrl+C is pressed

    except KeyboardInterrupt:
        print("Receiving stopped by user.")
    finally:
        # Close the client
        client.close()
