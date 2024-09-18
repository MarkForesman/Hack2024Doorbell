from azure.communication.email import EmailClient
import logging
from dotenv import load_dotenv
import os

load_dotenv(override=True)

def email_service(connection_string:str, sender_address: str, receiver_address: str, receiver_name: str):
    try:
        client = EmailClient.from_connection_string(connection_string)

        message = {
        "senderAddress": sender_address,
        "recipients": {
            "to": [
                {"address": receiver_address}
            ]
        },
        "content": {
            "subject": "Package Received!",
            "html": f"""
                <html>
                    <body>
                        <p>Hello {receiver_name}! A package has arrived for you.</p>
                        <img src="https://previews.123rf.com/images/aquir/aquir1311/aquir131100316/23569861-sample-grunge-red-round-stamp.jpg" alt="Image Description" />
                    </body>
                </html>
            """
        }
    }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        logging.error(ex)

email_service(connection_string=os.environ["EMAIL_COMMUNICATION_CONNECTION_STRING"], sender_address=os.environ["COMMUNICATION_SENDER_ADDRESS"], receiver_address="connorwehrum@microsoft.com")