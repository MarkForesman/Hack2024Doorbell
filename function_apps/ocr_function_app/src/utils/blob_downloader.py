from azure.storage.blob import BlobServiceClient

def download_blob_to_string(connection_string: str, container_name: str, blob_name: str) -> str:
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
    blob_client = blob_service_client.get_blob_client(
    container=container_name, blob=blob_name)
    blob_data = blob_client.download_blob().readall()
    return blob_data.decode('utf-8')
