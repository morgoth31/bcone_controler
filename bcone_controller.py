import asyncio
import json
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError
import paho.mqtt.client as mqtt
import time
import sys

# =============================================================================
# --- CONFIGURATION ---
# =============================================================================
def load_config():
    """Loads the configuration from config.json."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: config.json is not a valid JSON file.")
        sys.exit(1)

config = load_config()

# --- Bluetooth ---
TARGET_ADDRESS = config["bluetooth"]["target_address"]
READ_INTERVAL = config["bluetooth"]["read_interval"]

# --- MQTT ---
MQTT_BROKER_ADDRESS = config["mqtt"]["broker_address"]
MQTT_PORT = config["mqtt"]["port"]
MQTT_USERNAME = config["mqtt"]["username"]
MQTT_PASSWORD = config["mqtt"]["password"]

# --- Home Assistant ---
DEVICE_ID = config["home_assistant"]["device_id"]
DEVICE_NAME = config["home_assistant"]["device_name"]
# =============================================================================

# A dictionary of UUIDs for bluetooth characteristics, separated by access type.
CHARACTERISTIC_UUIDS = {
    "read": {
        "alarm_status": "82046727-0625-4196-aed0-f0e661b2eebd",
        "battery_level": "a3768c74-4489-4d82-b557-535f33614e2b",
        "temperature": "4d6cbd23-061b-47a2-b82c-cdbaaed98d63",
        "signal_attenuation": "9e887463-e6fd-4ff5-a366-6d2f42901a74",
    },
    "write": {
        "test_siren": "f7bf3564-fb6d-4e53-88a4-5e37e0326063",
        "sensitivity": "6362168c-c448-44db-b470-793832a3538b",
    },
    "read_write": {
        "mode": "1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb",
        "sensitivity": "6362168c-c448-44db-b470-793832154859",
        "standby_time": "734ecc1d-ed20-4a8c-8eeb-554476154852",
        "alarm_length": "734ecc1d-ed20-4a8c-8eeb-554476188831",
        "do_not_disturb_to": "734ecc1d-ed20-4a8c-8eeb-554476364285",
        "do_not_disturb_from": "734ecc1d-ed20-4a8c-8eeb-554476954872",
        "do_not_disturb_on_off": "e541793c-8a5e-4a5d-b6ff-c6b6c69244a1",
    },
}

# Mappage pour le contrôle du mode
MODE_MAP = {"ON": 1, "OFF": 2, "SWIM": 3}
MODE_MAP_REVERSE = {v: k for k, v in MODE_MAP.items()}

# --- Global Variables ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
ble_client_instance = None
main_loop = None

def on_connect(client, userdata, flags, rc, properties):
    """
    Callback for when the client receives a CONNACK response from the server.
    """
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(f"ble/{DEVICE_ID}/+/set")
        print(f"Subscribed to command topic: ble/{DEVICE_ID}/+/set")
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}\n")

def on_message(client, userdata, msg):
    """
    Callback for when a PUBLISH message is received from the server.
    """
    global ble_client_instance, main_loop
    
    command = msg.topic.split('/')[-2]
    payload = msg.payload.decode()
    print(f"Command '{command}' received with payload '{payload}'")

    if not (ble_client_instance and ble_client_instance.is_connected and main_loop):
        print("BLE client not connected, command ignored.")
        return

    uuid_key = None
    value_to_write = None

    try:
        if command == 'mode':
            uuid_key = "mode"
            mode_int = MODE_MAP.get(payload.upper())
            if mode_int is not None:
                value_to_write = bytearray([mode_int])
        elif command in ['standby_time', 'alarm_length', 'sensitivity', 'dnd_from', 'dnd_to']:
            uuid_key = command
            if command in ['dnd_from', 'dnd_to']:
                 value_to_write = int(float(payload)).to_bytes(2, 'little')
            else:
                 value_to_write = bytearray([int(float(payload))])
        
        if uuid_key and value_to_write is not None:
            uuid = CHARACTERISTIC_UUIDS["read_write"].get(uuid_key) or CHARACTERISTIC_UUIDS["write"].get(uuid_key)
            if uuid:
                print(f"Writing value {value_to_write.hex()} to UUID {uuid}...")
                asyncio.run_coroutine_threadsafe(
                    ble_client_instance.write_gatt_char(uuid, value_to_write),
                    main_loop
                )
            else:
                print(f"Error: UUID for command '{command}' not found.")
    except Exception as e:
        print(f"Error processing command '{command}': {e}")


def setup_mqtt_client():
    """
    Sets up and connects the MQTT client.
    """
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    try:
        mqtt_client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"Error connecting to MQTT: {e}")
        return False
    return True

def publish_ha_discovery():
    """
    Publishes all entity configurations for Home Assistant.
    """
    device_info = {"identifiers": [DEVICE_ID], "name": DEVICE_NAME, "manufacturer": "Lifebuoy LTD"}
    state_topic = f"ble/{DEVICE_ID}/state"

    # Sensor entities
    sensors = {
        "battery_level": {"name": "Battery Voltage", "unit": "V", "icon": "mdi:battery", "device_class": "voltage"},
        "temperature": {"name": "Temperature", "unit": "°C", "icon": "mdi:thermometer", "device_class": "temperature"},
        "alarm_status": {"name": "Alarm Status", "icon": "mdi:alarm-light"},
        "signal_attenuation": {"name": "Signal Attenuation", "unit": "dB", "icon": "mdi:signal", "device_class": "signal_strength"},
        "mode": {"name": "Mode Status", "icon": "mdi:cog-outline"},
        "sensitivity": {"name": "Sensitivity Status", "icon": "mdi:tune"},
        "standby_time": {"name": "Standby Time Status", "unit": "min", "icon": "mdi:timer-sand"},
        "alarm_length": {"name": "Alarm Length Status", "unit": "s", "icon": "mdi:timer"},
        "dnd_from": {"name": "DND From Status", "unit": "min", "icon": "mdi:timer-outline"},
        "dnd_to": {"name": "DND To Status", "unit": "min", "icon": "mdi:timer-outline"},
    }
    for key, config in sensors.items():
        topic = f"homeassistant/sensor/{DEVICE_ID}/{key}/config"
        payload = {"name": f"{DEVICE_NAME} {config['name']}", "state_topic": state_topic, "value_template": f"{{{{ value_json.{key} }}}}", "unique_id": f"{DEVICE_ID}_{key}", "device": device_info, "icon": config.get("icon", "")}
        if config.get("unit"): payload["unit_of_measurement"] = config["unit"]
        if config.get("device_class"): payload["device_class"] = config["device_class"]
        mqtt_client.publish(topic, json.dumps(payload), retain=True)

    # Select entity for mode
    select_payload = {"name": f"{DEVICE_NAME} Mode", "command_topic": f"ble/{DEVICE_ID}/mode/set", "state_topic": state_topic, "value_template": "{{ value_json.mode }}", "options": list(MODE_MAP.keys()), "unique_id": f"{DEVICE_ID}_mode", "device": device_info, "icon": "mdi:cog"}
    mqtt_client.publish(f"homeassistant/select/{DEVICE_ID}/mode/config", json.dumps(select_payload), retain=True)

    # Number entities (sliders)
    numbers = {
        "standby_time": {"name": "Standby Time", "min": 1, "max": 30, "step": 1, "unit": "min", "icon": "mdi:timer-sand"},
        "alarm_length": {"name": "Alarm Length", "min": 5, "max": 180, "step": 5, "unit": "s", "icon": "mdi:timer"},
        "sensitivity": {"name": "Sensitivity", "min": 1, "max": 5, "step": 1, "icon": "mdi:tune"},
        "dnd_from": {"name": "DND From", "min": 0, "max": 1439, "step": 1, "unit": "min", "icon": "mdi:timer-outline"},
        "dnd_to": {"name": "DND To", "min": 0, "max": 1439, "step": 1, "unit": "min", "icon": "mdi:timer-outline"},
    }
    for key, config in numbers.items():
        topic = f"homeassistant/number/{DEVICE_ID}/{key}/config"
        payload = {"name": f"{DEVICE_NAME} {config['name']}", "command_topic": f"ble/{DEVICE_ID}/{key}/set", "state_topic": state_topic, "value_template": f"{{{{ value_json.{key} }}}}", "min": config['min'], "max": config['max'], "step": config['step'], "unique_id": f"{DEVICE_ID}_{key}", "device": device_info, "icon": config.get("icon", "")}
        if config.get("unit"): payload["unit_of_measurement"] = config["unit"]
        mqtt_client.publish(topic, json.dumps(payload), retain=True)

async def read_ble_data(client):
    """
    Reads data from all readable BLE characteristics and returns a dictionary of the data.
    """
    sensor_data = {}

    # Read from "read" characteristics
    for key, uuid in CHARACTERISTIC_UUIDS["read"].items():
        try:
            value_bytes = await client.read_gatt_char(uuid)
            value_dec = int.from_bytes(value_bytes, "little")

            if key == "battery_level":
                sensor_data[key] = f"{value_dec / 100.0:.2f}"
            elif key == "temperature":
                sensor_data[key] = f"{value_dec / 100.0:.2f}"
            elif key == "alarm_status":
                sensor_data[key] = "Ringing!" if value_dec == 4 else "OFF"
            elif key == "signal_attenuation":
                sensor_data[key] = -value_dec
            else:
                sensor_data[key] = value_dec
        except Exception as e:
            print(f"Error reading {key}: {e}")

    # Read from "read_write" characteristics
    for key, uuid in CHARACTERISTIC_UUIDS["read_write"].items():
        try:
            value_bytes = await client.read_gatt_char(uuid)
            value_dec = int.from_bytes(value_bytes, "little")
            if key == "mode":
                sensor_data[key] = MODE_MAP_REVERSE.get(value_dec, "UNKNOWN")
            else:
                sensor_data[key] = value_dec
        except Exception as e:
            print(f"Error reading {key}: {e}")

    return sensor_data

async def main():
    """
    Main function to run the BLE to MQTT bridge.
    """
    global ble_client_instance, main_loop
    main_loop = asyncio.get_running_loop()

    if not setup_mqtt_client():
        return

    await asyncio.sleep(2)
    publish_ha_discovery()

    while True:
        try:
            print(f"Searching for device {TARGET_ADDRESS}...")
            device = await BleakScanner.find_device_by_address(TARGET_ADDRESS, timeout=10.0)
            if not device:
                print("Device not found, retrying in 60s...")
                await asyncio.sleep(60)
                continue

            async with BleakClient(device) as client:
                ble_client_instance = client
                print(f"Connected to {TARGET_ADDRESS}")
                
                while client.is_connected:
                    sensor_data = await read_ble_data(client)
                    
                    if sensor_data:
                        payload = json.dumps(sensor_data)
                        print(f"Publishing data: {payload}")
                        state_topic = f"ble/{DEVICE_ID}/state"
                        mqtt_client.publish(state_topic, payload)
                    
                    await asyncio.sleep(READ_INTERVAL)
        except BleakError as e:
            print(f"Bleak error: {e}. Reconnecting...")
        except Exception as e:
            print(f"Unexpected error: {e}. Reconnecting...")
        
        ble_client_instance = None
        await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script stopped.")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
