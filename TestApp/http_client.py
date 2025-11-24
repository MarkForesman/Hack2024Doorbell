"""
HTTP Client for Local Orchestrator
Replaces Azure IoT Hub client with local network communication
"""
import requests
from typing import Optional, Callable
import threading
import time
import os
from dotenv import load_dotenv
import json

load_dotenv(override=True)

class HttpClient:
    def __init__(self):
        self.orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")
        self.device_id = os.getenv("DEVICE_ID")
        self.device_type = os.getenv("DEVICE_MODE")  # Doorbell, Signaler, or LabelScanner
        
        if not self.device_id:
            raise ValueError("DEVICE_ID must be set in environment variables")
        if not self.device_type:
            raise ValueError("DEVICE_MODE must be set in environment variables")
        
        self._message_callback: Optional[Callable] = None
        self._polling_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()
        
        # Register device on initialization
        self._register_device()
        
    def _register_device(self):
        """Register this device with the orchestrator"""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/api/devices/register",
                json={
                    "device_id": self.device_id,
                    "device_type": self.device_type
                },
                timeout=5
            )
            response.raise_for_status()
            print(f"Device registered: {self.device_id} ({self.device_type})")
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not register device: {e}")
            print("Device will continue to operate but may not receive messages")
    
    def send_message(self, str_message: str):
        """Send a message/event to the orchestrator"""
        try:
            # Parse the JSON message
            message_data = json.loads(str_message)
            
            response = requests.post(
                f"{self.orchestrator_url}/api/events",
                json=message_data,
                timeout=5
            )
            response.raise_for_status()
            print(f"Message sent successfully: {str_message[:100]}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
        except json.JSONDecodeError as e:
            print(f"Error parsing message JSON: {e}")
    
    def receive(self, message_received_callback: Callable):
        """Set up callback for receiving messages and start polling"""
        print("Setting up message receive callback")
        self._message_callback = message_received_callback
        
        # Start polling thread
        self._stop_polling.clear()
        self._polling_thread = threading.Thread(target=self._poll_messages, daemon=True)
        self._polling_thread.start()
    
    def _poll_messages(self):
        """Poll the orchestrator for new messages"""
        while not self._stop_polling.is_set():
            try:
                response = requests.get(
                    f"{self.orchestrator_url}/api/devices/{self.device_id}/messages",
                    timeout=5
                )
                response.raise_for_status()
                
                data = response.json()
                messages = data.get("messages", [])
                
                # Process each message
                for message in messages:
                    if self._message_callback:
                        # Create a simple message object that mimics IoT Hub message
                        class Message:
                            def __init__(self, data):
                                self.data = json.dumps(data).encode('utf-8')
                        
                        msg = Message(message)
                        self._message_callback(msg)
                
            except requests.exceptions.RequestException as e:
                print(f"Error polling messages: {e}")
            
            # Poll every 2 seconds
            time.sleep(2)
    
    def disconnect(self):
        """Stop polling and disconnect"""
        print("Disconnecting HTTP client")
        self._stop_polling.set()
        if self._polling_thread:
            self._polling_thread.join(timeout=5)
    
    def upload_blob_file(self, file_name: str) -> dict:
        """Upload a file to the orchestrator (replaces Azure blob upload)"""
        try:
            with open(file_name, 'rb') as f:
                files = {'file': (file_name, f)}
                data = {
                    'device_id': self.device_id,
                    'filename': file_name
                }
                
                response = requests.post(
                    f"{self.orchestrator_url}/api/images/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                
                return {"status_code": 200, "status_description": "Upload successful"}
        
        except requests.exceptions.RequestException as e:
            print(f"Error uploading file: {e}")
            return {"status_code": 500, "status_description": str(e)}
