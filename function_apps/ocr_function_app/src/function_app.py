import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from utils.ocr import document_intelligence_ocr
from utils.fuzzy_search import extract_name_from_label
from utils.blob_downloader import download_blob_to_string
from models.employee import Employees
import logging
import os
import json
from dotenv import load_dotenv

# Configs
load_dotenv(override=True)
di_endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
di_key = os.environ["DOCUMENT_INTELLIGENCE_API_KEY"]
blob_connection_string = os.environ["STORAGE_ACCOUNT_CONNECTION_STRING"]
blob_container_name = os.environ["STORAGE_CONTAINER_NAME"]

# Clients
document_intelligence_client = DocumentAnalysisClient(endpoint=di_endpoint, credential=AzureKeyCredential(di_key))
app = func.FunctionApp()

# JSON employee data
json_data = download_blob_to_string(connection_string=blob_connection_string,
                            container_name=blob_container_name,
                            blob_name="employees.json")

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
    
    employees = Employees(**json.loads(json_data))

    names = [employee.name for employee in employees.employees]
    shipping_label = document_intelligence_ocr(document_analysis_client=document_intelligence_client, image_url=f"")
    fuzzy_result = extract_name_from_label(shipping_label=shipping_label, employee_list=names)
    if fuzzy_result is None:
        # TODO: Add logic to handle when it's None
        print("It's None")
        pass
    found_employee = employees.find_employee_by_name(fuzzy_result)
    print(f"It's a match! {found_employee}")
