#!/usr/bin/env python3
"""
CPU Temperature MQTT Subscriber
Subscribes to CPU temperature readings and displays them
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def get_temp_color(temperature):
    """Return appropriate color based on temperature"""
    if temperature < 50:
        return Colors.GREEN
    elif temperature < 60:
        return Colors.YELLOW
    else:
        return Colors.RED

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print("Connected to MQTT broker successfully")
        # Subscribe to the temperature topic
        client.subscribe("system/cpu/temperature")
        print("Subscribed to system/cpu/temperature")
        print("Waiting for temperature readings...")
        print("-" * 50)
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    try:
        # Decode the message payload
        payload = json.loads(msg.payload.decode())
        
        temperature = payload.get('temperature')
        unit = payload.get('unit', 'celsius')
        timestamp = payload.get('timestamp')
        
        # Parse and format timestamp for display
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
        else:
            time_str = datetime.now().strftime("%H:%M:%S")
        
        # Get color based on temperature
        color = get_temp_color(temperature)
        
        # Display the temperature reading with color
        print(f"[{time_str}] CPU Temperature: {color}{temperature}°{unit[0].upper()}{Colors.RESET}")
        
    except json.JSONDecodeError:
        # Handle plain text messages
        print(f"Received (raw): {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Raw message: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects"""
    print("\nDisconnected from MQTT broker")

def main():
    # MQTT Configuration
    BROKER_HOST = "localhost"
    BROKER_PORT = 1883
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        
        # Start the network loop to process callbacks
        print("Starting subscriber...")
        print("Press Ctrl+C to stop")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\nShutting down subscriber...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()