from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta

def download_blob_to_string(blob_service_client: BlobServiceClient, container_name: str, blob_name: str) -> str:
    blob_client = blob_service_client.get_blob_client(
    container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    return blob_data.decode('utf-8')

def generate_blob_sas_token(blob_service_client: BlobServiceClient, container_name: str, blob_name: str, account_key: str, expiry_duration_days: int = 30) -> str:
    
    # Set the expiry time for the SAS token
    expiry_time = datetime.utcnow() + timedelta(days=expiry_duration_days)

    # Generate the SAS token for the blob
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        permission="r",
        expiry=expiry_time,
        account_key=account_key
    )
    
    return sas_token
