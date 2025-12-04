"""
TCP Client for Local Orchestrator
Maintains persistent TCP connection and handles LED commands
"""
import socket
import threading
import json
import os
from dotenv import load_dotenv
from typing import Optional, Callable
import time

load_dotenv(override=True)

class TcpClient:
    def __init__(self):
        self.orchestrator_host = os.getenv("ORCHESTRATOR_HOST", "localhost")
        self.orchestrator_port = int(os.getenv("ORCHESTRATOR_PORT", "9999"))
        self.device_id = os.getenv("DEVICE_ID")
        self.device_type = os.getenv("DEVICE_MODE")  # Doorbell, Signaler, or LabelScanner
        
        if not self.device_id:
            raise ValueError("DEVICE_ID must be set in environment variables")
        if not self.device_type:
            raise ValueError("DEVICE_MODE must be set in environment variables")
        
        self.socket: Optional[socket.socket] = None
        self._message_callback: Optional[Callable] = None
        self._receive_thread: Optional[threading.Thread] = None
        self._stop_receiving = threading.Event()
        self._connected = False
        self._reconnect_thread: Optional[threading.Thread] = None
        
        # Connect to orchestrator
        self._connect()
        
    def _connect(self):
        """Establish connection to orchestrator"""
        retry_delay = 2
        max_retry_delay = 30
        attempt = 0
        
        while True:
            attempt += 1
            try:
                print(f"Attempting to connect to orchestrator at {self.orchestrator_host}:{self.orchestrator_port} (attempt {attempt})")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.orchestrator_host, self.orchestrator_port))
                self._connected = True
                print(f"Connected to orchestrator at {self.orchestrator_host}:{self.orchestrator_port}")
                
                # Register device
                self._register()
                
                # Start receive thread
                self._stop_receiving.clear()
                self._receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
                self._receive_thread.start()
                
                return
                
            except Exception as e:
                print(f"Connection attempt {attempt} failed: {e}")
                current_delay = min(retry_delay * (1.5 ** (attempt - 1)), max_retry_delay)
                print(f"Retrying in {current_delay:.1f} seconds...")
                time.sleep(current_delay)
    
    def _register(self):
        """Register this device with the orchestrator"""
        registration_msg = {
            'type': 'register',
            'device_id': self.device_id,
            'device_type': self.device_type
        }
        self._send_raw(registration_msg)
        print(f"Registration sent: {self.device_id} ({self.device_type})")
    
    def _send_raw(self, message: dict):
        """Send a raw message over the socket"""
        try:
            if self.socket and self._connected:
                message_str = json.dumps(message) + '\n'
                self.socket.sendall(message_str.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            self._connected = False
            self._attempt_reconnect()
    
    def send_message(self, str_message: str):
        """Send a message/event to the orchestrator"""
        try:
            # Parse the JSON message to get event details
            message_data = json.loads(str_message)
            button = message_data.get('Button', 1)
            
            # Map button to location: button 1 = back_door, button 2 = front_door
            location = 'back_door' if button == 1 else 'front_door'
            
            # Transform to orchestrator format
            button_press_msg = {
                'type': 'button_press',
                'device_id': self.device_id,
                'device_type': self.device_type,
                'button': button,
                'location': location
            }
            
            self._send_raw(button_press_msg)
            print(f"Button press sent: {button_press_msg}")
            
        except json.JSONDecodeError as e:
            print(f"Error parsing message JSON: {e}")
    
    def _receive_messages(self):
        """Receive messages from orchestrator in background thread"""
        buffer = ""
        
        while not self._stop_receiving.is_set() and self._connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    print("Connection closed by server")
                    self._connected = False
                    self._attempt_reconnect()
                    break
                
                buffer += data.decode('utf-8')
                
                # Process complete messages (delimited by newline)
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str:
                        self._handle_message(message_str)
                        
            except Exception as e:
                if self._connected:
                    print(f"Error receiving message: {e}")
                    self._connected = False
                    self._attempt_reconnect()
                break
    
    def _handle_message(self, message_str: str):
        """Handle incoming message from orchestrator"""
        try:
            message = json.loads(message_str)
            msg_type = message.get('type')
            
            if msg_type == 'registered':
                print(f"Device registration confirmed")
            
            elif msg_type == 'led_update':
                # Forward LED command to callback
                if self._message_callback:
                    # Create a message object that mimics IoT Hub format
                    class Message:
                        def __init__(self, data):
                            self.data = json.dumps(data).encode('utf-8')
                    
                    msg = Message(message)
                    self._message_callback(msg)
            
            else:
                print(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing received message: {e}")
    
    def receive(self, message_received_callback: Callable):
        """Set up callback for receiving LED commands"""
        print("Setting up message receive callback")
        self._message_callback = message_received_callback
    
    def _attempt_reconnect(self):
        """Attempt to reconnect to orchestrator"""
        if not self._reconnect_thread or not self._reconnect_thread.is_alive():
            self._reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
            self._reconnect_thread.start()
    
    def _reconnect_loop(self):
        """Reconnection loop"""
        retry_delay = 5
        while not self._connected and not self._stop_receiving.is_set():
            print("Attempting to reconnect...")
            try:
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                
                self._connect()
                
                # Re-register callback if it was set
                if self._message_callback:
                    print("Re-established message callback")
                    
                return
                
            except Exception as e:
                print(f"Reconnection failed: {e}")
                time.sleep(retry_delay)
    
    def disconnect(self):
        """Disconnect from orchestrator"""
        print("Disconnecting TCP client")
        self._stop_receiving.set()
        self._connected = False
        
        if self._receive_thread:
            self._receive_thread.join(timeout=2)
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def upload_blob_file(self, file_name: str) -> dict:
        """Send image metadata to orchestrator (actual file stored locally)"""
        try:
            upload_msg = {
                'type': 'image_upload',
                'device_id': self.device_id,
                'filename': file_name
            }
            
            self._send_raw(upload_msg)
            
            return {"status_code": 200, "status_description": "Metadata sent"}
        
        except Exception as e:
            print(f"Error sending image metadata: {e}")
            return {"status_code": 500, "status_description": str(e)}
