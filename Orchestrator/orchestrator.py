"""
TCP Socket Orchestrator for Doorbell System
Manages persistent TCP connections from doorbell devices
Routes messages and controls LED states across all devices
"""
import socket
import threading
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import select

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Connected clients: device_id -> {socket, device_type, address}
connected_clients: Dict[str, dict] = {}
# Lock for thread-safe operations
lock = threading.Lock()

# Doorbell state management
doorbell_states = {
    "front_door": {"pressed": False, "confirmed": False},
    "back_door": {"pressed": False, "confirmed": False}
}

class OrchestratorServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Start the TCP server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.running = True
        
        logger.info(f"Orchestrator server started on {self.host}:{self.port}")
        
        while self.running:
            try:
                # Accept new connections
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket: socket.socket, address):
        """Handle communication with a connected client"""
        device_id = None
        buffer = ""
        
        try:
            while self.running:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    logger.info(f"Client {device_id or address} disconnected")
                    break
                
                buffer += data.decode('utf-8')
                
                # Process complete messages (delimited by newline)
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message:
                        self.process_message(message, client_socket, address, device_id)
                        # Update device_id if this was a registration
                        if not device_id:
                            device_id = self.get_device_id_from_socket(client_socket)
        
        except Exception as e:
            logger.error(f"Error handling client {device_id or address}: {e}")
        
        finally:
            # Clean up
            with lock:
                if device_id and device_id in connected_clients:
                    del connected_clients[device_id]
                    logger.info(f"Device {device_id} removed from connected clients")
            
            try:
                client_socket.close()
            except:
                pass
    
    def get_device_id_from_socket(self, client_socket):
        """Find device_id by socket"""
        with lock:
            for dev_id, info in connected_clients.items():
                if info['socket'] == client_socket:
                    return dev_id
        return None
    
    def process_message(self, message: str, client_socket: socket.socket, address, device_id):
        """Process incoming message from client"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'register':
                self.handle_registration(data, client_socket, address)
            
            elif msg_type == 'button_press':
                self.handle_button_press(data)
            
            elif msg_type == 'image_upload':
                self.handle_image_metadata(data)
            
            elif msg_type == 'confirm_pickup':
                self.handle_pickup_confirmation(data)
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {device_id or address}: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def handle_registration(self, data: dict, client_socket: socket.socket, address):
        """Register a new device"""
        device_id = data.get('device_id')
        device_type = data.get('device_type')
        
        if not device_id or not device_type:
            logger.error(f"Invalid registration from {address}")
            return
        
        with lock:
            connected_clients[device_id] = {
                'socket': client_socket,
                'device_type': device_type,
                'address': address,
                'registered_at': datetime.utcnow().isoformat()
            }
        
        logger.info(f"Device registered: {device_id} ({device_type}) from {address}")
        
        # Send acknowledgment
        self.send_to_device(device_id, {'type': 'registered', 'status': 'ok'})
    
    def handle_button_press(self, data: dict):
        """Handle doorbell button press"""
        device_id = data.get('device_id')
        device_type = data.get('device_type')
        button = data.get('button', 1)
        location = data.get('location', 'front_door')
        
        logger.info(f"Button press: {device_id} ({device_type}) - {location}")
        
        if device_type == "Doorbell":
            # Update doorbell state
            doorbell_states[location]['pressed'] = True
            doorbell_states[location]['confirmed'] = False
            
            # Set doorbell LED to flashing red (handled by device)
            self.broadcast_led_update(device_type, "Doorbell", {
                'button': button,
                'red': 1,
                'green': 0,
                'blue': 0,
                'flash': True
            })
            
            # Notify signaler devices - light up corresponding LED
            self.broadcast_led_update(device_type, "Signaler", {
                'button': 1 if location == "back_door" else 2,
                'red': 1,
                'green': 0,
                'blue': 0,
                'reset_after': 500
            })
        
        elif device_type == "Signaler":
            # Signaler button press means package picked up
            self.handle_pickup_confirmation({
                'device_id': device_id,
                'location': 'back_door' if button == 1 else 'front_door'
            })
    
    def handle_pickup_confirmation(self, data: dict):
        """Handle package pickup confirmation"""
        location = data.get('location', 'front_door')
        
        logger.info(f"Package picked up at {location}")
        
        # Update state
        doorbell_states[location]['confirmed'] = True
        doorbell_states[location]['pressed'] = False
        
        # Turn off flashing on doorbell, set to green
        self.broadcast_led_update(None, "Doorbell", {
            'button': 1,
            'red': 0,
            'green': 1,
            'blue': 0,
            'flash': False,
            'reset_after': 60
        })
        
        # Set signaler LED to green
        button_num = 1 if location == "back_door" else 2
        self.broadcast_led_update(None, "Signaler", {
            'button': button_num,
            'red': 0,
            'green': 1,
            'blue': 0,
            'reset_after': 25
        })
    
    def handle_image_metadata(self, data: dict):
        """Handle image upload metadata from label scanner"""
        device_id = data.get('device_id')
        filename = data.get('filename')
        
        logger.info(f"Image scan from {device_id}: {filename}")
        
        # Could trigger package arrival event
        # For now, just log it
    
    def broadcast_led_update(self, exclude_device_id: Optional[str], target_device_type: str, led_command: dict):
        """Broadcast LED update to devices of specific type"""
        message = {
            'type': 'led_update',
            'command': led_command
        }
        
        with lock:
            for device_id, info in connected_clients.items():
                if info['device_type'] == target_device_type:
                    if exclude_device_id is None or device_id != exclude_device_id:
                        self.send_to_device(device_id, message)
    
    def send_to_device(self, device_id: str, message: dict):
        """Send message to a specific device"""
        with lock:
            if device_id not in connected_clients:
                logger.warning(f"Device {device_id} not connected")
                return
            
            client_socket = connected_clients[device_id]['socket']
        
        try:
            message_str = json.dumps(message) + '\n'
            client_socket.sendall(message_str.encode('utf-8'))
            logger.debug(f"Sent to {device_id}: {message}")
        except Exception as e:
            logger.error(f"Error sending to {device_id}: {e}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

if __name__ == '__main__':
    server = OrchestratorServer(host='0.0.0.0', port=9999)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop()
