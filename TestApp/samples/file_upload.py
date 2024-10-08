# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import sys
import uuid
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
import pprint
from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceExistsError
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
Welcome to the Upload to Blob sample for the Azure IoT Device Library for Python. To use this sample you must have azure.storage.blob installed in your python environment.
To do this, you can run:
    $ pip install azure.storage.blob
This sample covers using the following Device Client APIs:
    get_storage_info_for_blob
        - used to get relevant information from IoT Hub about a linked Storage Account, including
        a hostname, a container name, a blob name, and a sas token. Additionally it returns a correlation_id
        which is used in the notify_blob_upload_status, since the correlation_id is IoT Hub's way of marking
        which blob you are working on.
    notify_blob_upload_status
        - used to notify IoT Hub of the status of your blob storage operation. This uses the correlation_id obtained
        by the get_storage_info_for_blob task, and will tell IoT Hub to notify any service that might be listening for a notification on the
        status of the file upload task.
You can learn more about File Upload with IoT Hub here:
https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-file-upload
"""
IOTHUB_DEVICE_CONNECTION_STRING = os.getenv("IOT_CONNECTION_STRING")


async def upload_via_storage_blob(blob_info, file_name):
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


async def main():
    file_name=sys.argv[1]
    conn_str = IOTHUB_DEVICE_CONNECTION_STRING
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)    
    # Connect the client.
    await device_client.connect()

    # get the Storage SAS information from IoT Hub.
    storage_info = await device_client.get_storage_info_for_blob(file_name)
    result = {"status_code": -1, "status_description": "N/A"}

    # Using the Storage Blob V12 API, perform the blob upload.
    try:
        upload_result = await upload_via_storage_blob(storage_info, file_name)
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
        await device_client.notify_blob_upload_status(
            storage_info["correlationId"], True, result["status_code"], result["status_description"]
        )
    else:
        await device_client.notify_blob_upload_status(
            storage_info["correlationId"],
            False,
            result["status_code"],
            result["status_description"],
        )

    # Finally, shut down the client
    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
