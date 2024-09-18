import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from services.ocr_service import document_intelligence_ocr
from utils.fuzzy_search import extract_name_from_label
from services.blob_downloader_service import download_blob_to_string, generate_blob_sas_token
from services.email_service import send_email_service
from models.employee import Employees
from models.queue_message import PackageLabelScanEvent
import logging
import os
import json
from dotenv import load_dotenv

# Configs
load_dotenv(override=True)
di_endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
di_key = os.environ["DOCUMENT_INTELLIGENCE_API_KEY"]
blob_connection_string = os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"]
str_account_key = os.environ["STORAGE_ACCOUNT_KEY"]
str_config_container_name = os.environ["CONFIG_STORAGE_CONTAINER_NAME"]
str_devices_container_name = os.environ["DEVICES_CONTAINER_NAME"]
email_connection_string=os.environ["EMAIL_COMMUNICATION_CONNECTION_STRING"]
sender_address=os.environ["COMMUNICATION_SENDER_ADDRESS"]

# Clients
document_intelligence_client = DocumentAnalysisClient(endpoint=di_endpoint, credential=AzureKeyCredential(di_key))
blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
app = func.FunctionApp()

# JSON employee data
employee_json_data = download_blob_to_string(blob_service_client=blob_service_client,
                            container_name=str_config_container_name,
                            blob_name="employees.json")
employees = Employees(**json.loads(employee_json_data))

@app.function_name(name="QueueFunc")
@app.queue_trigger(arg_name="msg", queue_name="packagelabels",connection="AzureWebJobsStorage")  # Queue trigger
def package_notifier(msg: func.QueueMessage) -> None:
    """Looks for a device id and file image name from a queue message.
    Extracts the shipping label information and sends an email notification
    to a specific users alias if a match is found. If not, sends a email
    to a group alias.

    Args:
        msg (func.QueueMessage): TODO: **TBA**
    """
    
    logging.info('Python queue trigger function processed a queue item: %s', msg.get_body().decode('utf-8'))
    
    message_body = msg.get_body().decode('utf-8')
    message_dict = json.loads(message_body)
    event = PackageLabelScanEvent(**message_dict)
    event.Payload.Path
    blob_name = f"{event.Payload.DeviceId}/{event.Payload.Path}".strip()
    print(blob_name)
    blob_sas = generate_blob_sas_token(blob_service_client=blob_service_client,
                                           container_name=str_devices_container_name,
                                           blob_name=blob_name,
                                           account_key=str_account_key)

    
    blob_url = f"{blob_service_client.url}{str_devices_container_name}/{blob_name}?{blob_sas}".strip()
    print(blob_url)

    names = [employee.name for employee in employees.employees]
    
    print(blob_url)
    shipping_label = document_intelligence_ocr(document_analysis_client=document_intelligence_client, image_url=blob_url) # TODO: Add logic to extract file name and build url
    fuzzy_result = extract_name_from_label(shipping_label=shipping_label, employee_list=names)
    if fuzzy_result is None:
        # TODO: Add logic to handle when it's None
        print("It's None")
        pass
    found_employee = employees.find_employee_by_name(fuzzy_result)
    print(found_employee.name)
    send_email_service(connection_string=email_connection_string, sender_address=sender_address, employee=found_employee, image_url=blob_url) # TODO: Add image url
