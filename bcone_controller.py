import asyncio
import json
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError
import paho.mqtt.client as mqtt
import time

# =============================================================================
# --- CONFIGURATION ---
# =============================================================================
# --- Bluetooth ---
TARGET_ADDRESS = "B4:3A:31:E4:14:FB"
READ_INTERVAL = 60 

# --- MQTT ---
MQTT_BROKER_ADDRESS = "192.168.1.62"
MQTT_PORT = 1883
MQTT_USERNAME = "mqttuser"
MQTT_PASSWORD = "mqttpassword"

# --- Home Assistant ---
DEVICE_ID = "lifebuoy_alarm_01" 
DEVICE_NAME = "Alarme Lifebuoy"
# =============================================================================

# Dictionnaire des UUIDs mis à jour avec lecture/écriture séparées
CHARACTERISTIC_UUIDS = {
    # Capteurs (lecture seule)
    "ALARM_STATUS_READ": "82046727-0625-4196-aed0-f0e661b2eebd",
    "BATTERY_LEVEL_READ": "a3768c74-4489-4d82-b557-535f33614e2b",
    "TEMPERATURE_READ": "4d6cbd23-061b-47a2-b82c-cdbaaed98d63",
    "SIGNAL_ATTENUATION_READ": "9e887463-e6fd-4ff5-a366-6d2f42901a74",
    
    # Lecture/Écriture
    "MODE_READ": "1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb",
    "MODE_WRITE": "1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb", # Supposant que c'est le même
    "SENSITIVITY_READ": "6362168c-c448-44db-b470-793832154859",
    "SENSITIVITY_WRITE": "6362168c-c448-44db-b470-793832a3538b",
    "STANDBY_TIME_READ": "734ecc1d-ed20-4a8c-8eeb-554476154852",
    "STANDBY_TIME_WRITE": "734ecc1d-ed20-4a8c-8eeb-554476154852",
    "ALARM_LENGTH_READ": "734ecc1d-ed20-4a8c-8eeb-554476188831",
    "ALARM_LENGTH_WRITE": "734ecc1d-ed20-4a8c-8eeb-554476188831",
    "DO_NOT_DISTURB_TO_READ": "734ecc1d-ed20-4a8c-8eeb-554476364285",
    "DO_NOT_DISTURB_TO_WRITE": "734ecc1d-ed20-4a8c-8eeb-554476364285",
    "DO_NOT_DISTURB_FROM_READ": "734ecc1d-ed20-4a8c-8eeb-554476954872",
    "DO_NOT_DISTURB_FROM_WRITE": "734ecc1d-ed20-4a8c-8eeb-554476954872",
    "DO_NOT_DISTURB_ON_OFF_READ": "e541793c-8a5e-4a5d-b6ff-c6b6c69244a1",
    "DO_NOT_DISTURB_ON_OFF_WRITE": "e541793c-8a5e-4a5d-b6ff-c6b6c69244a1",

    # Écriture seule
    "TEST_SIREN_WRITE": "f7bf3564-fb6d-4e53-88a4-5e37e0326063",
}

# Mappage pour le contrôle du mode
MODE_MAP = {"ON": 1, "OFF": 2, "SWIM": 3}
MODE_MAP_REVERSE = {v: k for k, v in MODE_MAP.items()}

# --- Variables Globales ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
ble_client_instance = None
main_loop = None

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connecté au broker MQTT avec succès.")
        client.subscribe(f"ble/{DEVICE_ID}/+/set")
        print(f"Abonné au topic de commande : ble/{DEVICE_ID}/+/set")
    else:
        print(f"Échec de la connexion au broker MQTT, code de retour : {rc}")

def on_message(client, userdata, msg):
    """Gère les messages MQTT entrants pour contrôler l'appareil."""
    global ble_client_instance, main_loop
    
    command = msg.topic.split('/')[-2]
    payload = msg.payload.decode()
    print(f"Commande '{command}' reçue avec la valeur '{payload}'")

    if not (ble_client_instance and ble_client_instance.is_connected and main_loop):
        print("Client BLE non connecté, commande ignorée.")
        return

    uuid_key = None
    value_to_write = None

    try:
        if command == 'mode':
            uuid_key = "MODE_WRITE"
            mode_int = MODE_MAP.get(payload.upper())
            if mode_int is not None:
                value_to_write = bytearray([mode_int])
        elif command in ['standby_time', 'alarm_length', 'sensitivity', 'dnd_from', 'dnd_to']:
            uuid_key = f"{command.upper()}_WRITE"
            # Pour les temps, la valeur est en minutes, envoyée comme entier sur 2 octets
            if command in ['dnd_from', 'dnd_to']:
                 value_to_write = int(float(payload)).to_bytes(2, 'little')
            else: # Pour les autres, un seul octet suffit
                 value_to_write = bytearray([int(float(payload))])
        
        if uuid_key and value_to_write is not None:
            uuid = CHARACTERISTIC_UUIDS[uuid_key]
            print(f"Envoi de la valeur {value_to_write.hex()} à l'UUID {uuid}...")
            asyncio.run_coroutine_threadsafe(
                ble_client_instance.write_gatt_char(uuid, value_to_write),
                main_loop
            )
    except Exception as e:
        print(f"Erreur lors du traitement de la commande '{command}': {e}")


def setup_mqtt_client():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    try:
        mqtt_client.connect(MQTT_BROKER_ADDRESS, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"Erreur de connexion MQTT: {e}")
        return False
    return True

def publish_ha_discovery():
    """Publie toutes les configurations d'entités pour Home Assistant."""
    device_info = {"identifiers": [DEVICE_ID], "name": DEVICE_NAME, "manufacturer": "Lifebuoy LTD"}
    state_topic = f"ble/{DEVICE_ID}/state"

    # Entités de type "sensor"
    sensors = {
        "battery_level": {"name": "Tension Batterie", "unit": "V", "icon": "mdi:battery", "device_class": "voltage"},
        "temperature": {"name": "Température", "unit": "°C", "icon": "mdi:thermometer", "device_class": "temperature"},
        "alarm_status": {"name": "Statut Alarme", "icon": "mdi:alarm-light"},
        "signal_attenuation": {"name": "Atténuation Signal", "unit": "dB", "icon": "mdi:signal", "device_class": "signal_strength"},
        "mode_read": {"name": "Statut Mode", "icon": "mdi:cog-outline"},
        "sensitivity_read": {"name": "Statut Sensibilité", "icon": "mdi:tune"},
        "standby_time_read": {"name": "Statut Temps de Veille", "unit": "min", "icon": "mdi:timer-sand"},
        "alarm_length_read": {"name": "Statut Durée Alarme", "unit": "s", "icon": "mdi:timer"},
        "dnd_from_read": {"name": "Statut DND (De)", "unit": "min", "icon": "mdi:timer-outline"},
        "dnd_to_read": {"name": "Statut DND (À)", "unit": "min", "icon": "mdi:timer-outline"},
    }
    for key, config in sensors.items():
        topic = f"homeassistant/sensor/{DEVICE_ID}/{key}/config"
        payload = {"name": f"{DEVICE_NAME} {config['name']}", "state_topic": state_topic, "value_template": f"{{{{ value_json.{key} }}}}", "unique_id": f"{DEVICE_ID}_{key}", "device": device_info, "icon": config.get("icon", "")}
        if config.get("unit"): payload["unit_of_measurement"] = config["unit"]
        if config.get("device_class"): payload["device_class"] = config["device_class"]
        mqtt_client.publish(topic, json.dumps(payload), retain=True)

    # Entités de type "select" pour le mode
    select_payload = {"name": f"{DEVICE_NAME} Mode", "command_topic": f"ble/{DEVICE_ID}/mode/set", "state_topic": state_topic, "value_template": "{{ value_json.mode_read }}", "options": list(MODE_MAP.keys()), "unique_id": f"{DEVICE_ID}_mode", "device": device_info, "icon": "mdi:cog"}
    mqtt_client.publish(f"homeassistant/select/{DEVICE_ID}/mode/config", json.dumps(select_payload), retain=True)

    # Entités de type "number" (curseurs)
    numbers = {
        "standby_time": {"name": "Temps de Veille", "min": 1, "max": 30, "step": 1, "unit": "min", "icon": "mdi:timer-sand"},
        "alarm_length": {"name": "Durée Alarme", "min": 5, "max": 180, "step": 5, "unit": "s", "icon": "mdi:timer"},
        "sensitivity": {"name": "Sensibilité", "min": 1, "max": 5, "step": 1, "icon": "mdi:tune"},
        "dnd_from": {"name": "DND (De)", "min": 0, "max": 1439, "step": 1, "unit": "min", "icon": "mdi:timer-outline"},
        "dnd_to": {"name": "DND (À)", "min": 0, "max": 1439, "step": 1, "unit": "min", "icon": "mdi:timer-outline"},
    }
    for key, config in numbers.items():
        topic = f"homeassistant/number/{DEVICE_ID}/{key}/config"
        payload = {"name": f"{DEVICE_NAME} {config['name']}", "command_topic": f"ble/{DEVICE_ID}/{key}/set", "state_topic": state_topic, "value_template": f"{{{{ value_json.{key}_read }}}}", "min": config['min'], "max": config['max'], "step": config['step'], "unique_id": f"{DEVICE_ID}_{key}", "device": device_info, "icon": config.get("icon", "")}
        if config.get("unit"): payload["unit_of_measurement"] = config["unit"]
        mqtt_client.publish(topic, json.dumps(payload), retain=True)

async def main():
    global ble_client_instance, main_loop
    main_loop = asyncio.get_running_loop()

    if not setup_mqtt_client(): return
    await asyncio.sleep(2)
    publish_ha_discovery()

    while True:
        try:
            print(f"Recherche de l'appareil {TARGET_ADDRESS}...")
            device = await BleakScanner.find_device_by_address(TARGET_ADDRESS, timeout=10.0)
            if not device: print("Appareil introuvable, nouvelle tentative dans 60s..."); await asyncio.sleep(60); continue

            async with BleakClient(device) as client:
                ble_client_instance = client
                print(f"Connecté à {TARGET_ADDRESS}")
                
                while client.is_connected:
                    sensor_data = {}
                    for key, uuid in CHARACTERISTIC_UUIDS.items():
                        if "WRITE" in key and "READ" not in key: continue
                        try:
                            value_bytes = await client.read_gatt_char(uuid)
                            value_dec = int.from_bytes(value_bytes, "little")

                            # Formatage et mappage des valeurs
                            if key == "BATTERY_LEVEL_READ": sensor_data[key.lower()] = f"{value_dec / 100.0:.2f}"
                            elif key == "TEMPERATURE_READ": sensor_data[key.lower()] = f"{value_dec / 100.0:.2f}"
                            elif key == "ALARM_STATUS_READ": sensor_data[key.lower()] = "SONNE !" if value_dec == 4 else "OFF"
                            elif key == "SIGNAL_ATTENUATION_READ": sensor_data[key.lower()] = -value_dec
                            elif key == "MODE_READ": sensor_data[key.lower()] = MODE_MAP_REVERSE.get(value_dec, "UNKNOWN")
                            else: sensor_data[key.lower()] = value_dec
                        except Exception as e: print(f"Erreur de lecture pour {key}: {e}")
                    
                    if sensor_data:
                        payload = json.dumps(sensor_data)
                        print(f"Publication des données : {payload}")
                        mqtt_client.publish(state_topic, payload)
                    
                    await asyncio.sleep(READ_INTERVAL)
        except BleakError as e: print(f"Erreur Bleak: {e}. Tentative de reconnexion...")
        except Exception as e: print(f"Erreur inattendue: {e}. Tentative de reconnexion...")
        
        ble_client_instance = None
        await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script arrêté.")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
