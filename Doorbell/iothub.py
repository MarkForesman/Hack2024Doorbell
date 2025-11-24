from azure.iot.device import IoTHubDeviceClient, Message
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceExistsError
from dotenv import load_dotenv
import pprint
import os
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
       print("recieved") 
       self.client.on_message_received = message_received_callback
    
    def disconnect(self):
        self.client.shutdown()
    
    def upload_via_storage_blob(self, blob_info, file_name):
        """Helper function written to perform Storage Blob V12 Upload Tasks

        Arguments:
        blob_info - an object containing the information needed to generate a sas_url for creating a blob client

        Returns:
        status of blob upload operation, in the storage provided structure.
        """

        print("Azure Blob storage v12 - Python quickstart sample")
        sas_url = "https://{}/{}/{}{}".format(
            blob_info["hostName"],
            blob_info["containerName"],
            blob_info["blobName"],
            blob_info["sasToken"],
        )
        blob_client = BlobClient.from_blob_url(sas_url)


        # Perform the actual upload for the data.
        print("\nUploading to Azure Storage as blob:\n\t" + file_name)
        # # Upload the created file
        with open(file_name, "rb") as data:
            result = blob_client.upload_blob(data)

        return result
    
    def upload_blob_file(self, file_name: str):
        # get the Storage SAS information from IoT Hub.
        storage_info = self.client.get_storage_info_for_blob(file_name)
        result = {"status_code": -1, "status_description": "N/A"}

        # Using the Storage Blob V12 API, perform the blob upload.
        try:
            upload_result = self.upload_via_storage_blob(storage_info, file_name)
            if hasattr(upload_result, "error_code"):
                result = {
                    "status_code": upload_result.error_code,
                    "status_description": "Storage Blob Upload Error",
                }
            else:
                result = {"status_code": 200, "status_description": ""}
        except ResourceExistsError as ex:
            if ex.status_code:
                result = {"status_code": ex.status_code, "status_description": ex.reason}
            else:
                print("Failed with Exception: {}", ex)
                result = {"status_code": 400, "status_description": ex.message}

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)

        if result["status_code"] == 200:
            self.client.notify_blob_upload_status(
                storage_info["correlationId"], True, result["status_code"], result["status_description"]
            )
        else:
            self.client.notify_blob_upload_status(
                storage_info["correlationId"],
                False,
                result["status_code"],
                result["status_description"],
            )
        return result
