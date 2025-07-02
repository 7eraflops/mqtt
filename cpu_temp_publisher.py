#!/usr/bin/env python3
"""
CPU Temperature MQTT Publisher
Reads CPU temperature from thermal_zone0 and publishes to MQTT
"""

import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

def read_cpu_temp():
    """Read CPU temperature from thermal_zone0"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_raw = int(f.read().strip())
            # Convert from millidegrees to degrees Celsius
            temp_celsius = temp_raw / 1000.0
            return round(temp_celsius, 1)
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print("Connected to MQTT broker successfully")
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")

def main():
    # MQTT Configuration
    BROKER_HOST = "localhost"
    BROKER_PORT = 1883
    TOPIC_TEMP = "system/cpu/temperature"
    
    # Create MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
        
        print("Starting CPU temperature monitoring...")
        print("Press Ctrl+C to stop")
        
        while True:
            # Read CPU temperature
            cpu_temp = read_cpu_temp()
            
            if cpu_temp is not None:
                # Create message payload
                timestamp = datetime.now().isoformat()
                payload = {
                    "temperature": cpu_temp,
                    "unit": "celsius",
                    "timestamp": timestamp
                }
                
                # Publish temperature data
                result = client.publish(TOPIC_TEMP, json.dumps(payload))
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"Published: {cpu_temp}°C")
                else:
                    print(f"Failed to publish temperature data")
                    
            else:
                print("Could not read CPU temperature")
                
            # Wait 3 seconds before next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nShutting down publisher...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()