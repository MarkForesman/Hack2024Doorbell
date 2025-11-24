# TCP-Based Doorbell System Architecture

## Overview

This system has been refactored to use TCP sockets instead of Azure IoT Hub. The orchestrator runs as a TCP server on the local network, and each doorbell device connects as a TCP client.

## Architecture Components

### 1. Orchestrator Server (`orchestrator_tcp.py`)
- **Location**: Runs on a server/computer on the local network
- **Port**: 9999 (configurable)
- **Function**: 
  - Manages persistent TCP connections from all devices
  - Routes button press events between devices
  - Controls LED states across all devices
  - Maintains doorbell state (front door, back door)

### 2. Device Clients (Raspberry Pi devices)
- **Doorbell**: Detects button presses, sends events to orchestrator, receives LED commands
- **Signaler**: Receives package arrival notifications, allows package pickup confirmation
- **LabelScanner**: Scans package labels, uploads metadata to orchestrator

## Communication Protocol

### Message Format
All messages are JSON objects delimited by newline (`\n`)

### Message Types

#### Device → Orchestrator

**Registration**:
```json
{
  "type": "register",
  "device_id": "device-101",
  "device_type": "Doorbell"
}
```

**Button Press**:
```json
{
  "type": "button_press",
  "device_id": "device-101",
  "device_type": "Doorbell",
  "button": 1,
  "location": "front_door"
}
```

**Image Upload Metadata**:
```json
{
  "type": "image_upload",
  "device_id": "device-103",
  "filename": "abc123.jpg"
}
```

#### Orchestrator → Device

**Registration Confirmation**:
```json
{
  "type": "registered",
  "status": "ok"
}
```

**LED Update**:
```json
{
  "type": "led_update",
  "command": {
    "button": 1,
    "red": 1,
    "green": 0,
    "blue": 0,
    "flash": true,
    "reset_after": 60
  }
}
```

## Event Flow

### Doorbell Press Scenario

1. **User presses doorbell button**
   - Device sends `button_press` event to orchestrator
   
2. **Orchestrator processes event**
   - Updates internal state (front_door or back_door pressed)
   - Broadcasts LED update to Doorbell devices (red flashing)
   - Broadcasts LED update to Signaler devices (red solid on corresponding button)

3. **Package pickup (Signaler button press)**
   - Signaler sends `button_press` event
   - Orchestrator broadcasts LED update to all devices:
     - Doorbell: Stop flashing, turn green briefly
     - Signaler: Turn green briefly
   - State reset after timeout

## Setup Instructions

### Orchestrator Server Setup

1. **Install on a computer on the local network**:
```bash
cd Orchestrator
pip install -r requirements.txt
```

2. **Run the orchestrator**:
```bash
python orchestrator_tcp.py
```

The server will start on `0.0.0.0:9999` and listen for connections.

### Device Setup (Raspberry Pi)

1. **Configure environment variables** (`.env` file):
```env
DEVICE_ID=device-101
DEVICE_MODE=Doorbell  # or Signaler, LabelScanner
ORCHESTRATOR_HOST=192.168.1.100  # IP of orchestrator server
ORCHESTRATOR_PORT=9999
```

2. **Install dependencies**:
```bash
cd TestApp
pip install -r requirements.txt
```

3. **Run the device**:
```bash
python main.py
```

## Device Types

### Doorbell
- **Environment**: `DEVICE_MODE=Doorbell`
- **Buttons**: 1 or 2 (could represent different entrances)
- **LEDs**: Flashes red when pressed, green when confirmed
- **Behavior**: 
  - Button press sends event to orchestrator
  - Orchestrator controls LED state (flashing vs solid)

### Signaler
- **Environment**: `DEVICE_MODE=Signaler`
- **Buttons**: 
  - Button 1 = Back door package pickup
  - Button 2 = Front door package pickup
- **LEDs**: 
  - Lights red when package arrives
  - Lights green when pickup confirmed
- **Behavior**:
  - Receives LED updates when doorbell pressed
  - Button press confirms package pickup

### LabelScanner
- **Environment**: `DEVICE_MODE=LabelScanner`
- **Function**: Captures images and sends metadata to orchestrator
- **LEDs**: Yellow during scan, green on success

## Network Requirements

- All devices must be on the same local network
- Orchestrator must be reachable by all devices
- Firewall must allow TCP connections on port 9999
- Static IP recommended for orchestrator server

## Advantages Over IoT Hub

1. **No Cloud Dependency**: Fully local operation
2. **Lower Latency**: Direct TCP communication
3. **No Cloud Costs**: No Azure subscription needed
4. **Persistent Connections**: Real-time LED updates
5. **Simpler Architecture**: Single orchestrator manages all state
6. **Better Control**: Full visibility into device states

## LED State Management

The orchestrator centrally manages all LED states:

| Event | Doorbell LED | Signaler LED |
|-------|--------------|--------------|
| Button press (front door) | Red flashing | Button 2 red solid |
| Button press (back door) | Red flashing | Button 1 red solid |
| Package picked up (front) | Green (60s) | Button 2 green (25s) |
| Package picked up (back) | Green (60s) | Button 1 green (25s) |

## Troubleshooting

### Device Can't Connect
- Check `ORCHESTRATOR_HOST` IP address
- Verify orchestrator is running
- Check firewall settings
- Verify network connectivity: `ping <orchestrator_ip>`

### No LED Updates
- Check device type configuration
- Verify message routing in orchestrator logs
- Check device receive callback is registered

### Connection Drops
- TCP client has automatic reconnection
- Check network stability
- Review orchestrator logs for errors

## File Structure

```
Hack2024Doorbell/
├── Orchestrator/
│   ├── orchestrator_tcp.py      # TCP server
│   └── requirements.txt
└── TestApp/
    ├── tcp_client.py            # TCP client library
    ├── main.py                  # Device initialization
    ├── doorbell.py              # Doorbell device class
    ├── signaler.py              # Signaler device class
    ├── label_scanner.py         # Scanner device class
    ├── events.py                # Event data models
    └── requirements.txt
```

## Future Enhancements

- Web dashboard for orchestrator status
- Persistent storage of events
- Integration with cloud backend (optional)
- Multiple orchestrators for redundancy
- Encryption for TCP communication (TLS)
- Device authentication
