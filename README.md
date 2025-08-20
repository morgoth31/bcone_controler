# bcone_controller: BLE to MQTT Bridge for Lifebuoy Alarms

`bcone_controller` is a Python script that acts as a bridge between a Lifebuoy Bluetooth Low Energy (BLE) alarm device and a Home Assistant installation. It uses the `bleak` library to communicate with the BLE device and `paho-mqtt` to send and receive messages from an MQTT broker. The script automatically discovers and configures entities in Home Assistant using the MQTT discovery protocol.

## Features

-   Connects to a Lifebuoy BLE alarm device.
-   Reads sensor data (battery level, temperature, alarm status, etc.).
-   Allows controlling the device (mode, sensitivity, etc.) via MQTT.
-   Integrates with Home Assistant via MQTT discovery.
-   Configuration via a simple `config.json` file.

## Prerequisites

-   Python 3.7+
-   A Bluetooth adapter on the machine running the script.
-   An MQTT broker (e.g., Mosquitto).
-   Home Assistant with MQTT integration configured.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/bcone_controller.git
    cd bcone_controller
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the script, you need to create a `config.json` file in the same directory. You can use the provided `config.example.json` as a template.

1.  **Copy the example configuration:**
    ```bash
    cp config.example.json config.json
    ```

2.  **Edit `config.json` with your settings:**

    ```json
    {
        "bluetooth": {
            "target_address": "B4:3A:31:E4:14:FB",
            "read_interval": 60
        },
        "mqtt": {
            "broker_address": "192.168.1.62",
            "port": 1883,
            "username": "mqttuser",
            "password": "mqttpassword"
        },
        "home_assistant": {
            "device_id": "lifebuoy_alarm_01",
            "device_name": "Alarme Lifebuoy"
        }
    }
    ```

    -   `target_address`: The MAC address of your Lifebuoy BLE device.
    -   `read_interval`: The interval in seconds at which the script reads data from the device.
    -   `broker_address`, `port`, `username`, `password`: Your MQTT broker credentials.
    -   `device_id`, `device_name`: The ID and name for the device in Home Assistant.

## Usage

To run the script, simply execute the following command from the project directory:

```bash
python bcone_controller.py
```

The script will start, connect to the MQTT broker, and then begin searching for the BLE device. Once connected, it will start publishing data to MQTT and listening for commands.

## Home Assistant Integration

The script uses MQTT discovery to automatically create entities in Home Assistant. Once the script is running, you should see a new device in your Home Assistant instance with the following entities:

### Sensors

-   **Battery Voltage:** The current battery voltage of the device.
-   **Temperature:** The temperature measured by the device.
-   **Alarm Status:** The status of the alarm (e.g., "OFF", "Ringing!").
-   **Signal Attenuation:** The signal strength in dB.
-   **Mode Status:** The current mode of the device (e.g., "ON", "OFF", "SWIM").
-   **Sensitivity Status:** The current sensitivity level.
-   **Standby Time Status:** The current standby time setting.
-   **Alarm Length Status:** The current alarm length setting.
-   **DND From Status:** The start time for "Do Not Disturb" mode.
-   **DND To Status:** The end time for "Do Not Disturb" mode.

### Controls

-   **Mode:** A dropdown to select the device mode (`ON`, `OFF`, `SWIM`).
-   **Standby Time:** A slider to set the standby time (1-30 minutes).
-   **Alarm Length:** A slider to set the alarm duration (5-180 seconds).
-   **Sensitivity:** A slider to set the sensitivity (1-5).
-   **DND From:** A slider to set the "Do Not Disturb" start time.
-   **DND To:** A slider to set the "Do Not Disturb" end time.

## Bluetooth Characteristics

The following table details the Bluetooth characteristics used by this script.

| Name                  | UUID                                     | Permissions | Data Type/Range                               |
| --------------------- | ---------------------------------------- | ----------- | --------------------------------------------- |
| **Read-Only**         |                                          |             |                                               |
| Alarm Status          | `82046727-0625-4196-aed0-f0e661b2eebd`     | Read        | `4` (Ringing), `0` (Off)                      |
| Battery Level         | `a3768c74-4489-4d82-b557-535f33614e2b`     | Read        | Integer (e.g., `2917` for `2.917V`)           |
| Temperature           | `4d6cbd23-061b-47a2-b82c-cdbaaed98d63`     | Read        | Integer (e.g., `27` for `27°C`)               |
| Signal Attenuation    | `9e887463-e6fd-4ff5-a366-6d2f42901a74`     | Read        | Integer (dB)                                  |
| **Write-Only**        |                                          |             |                                               |
| Test Siren            | `f7bf3564-fb6d-4e53-88a4-5e37e0326063`     | Write       | `1` (Test)                                    |
| Sensitivity (Write)   | `6362168c-c448-44db-b470-793832a3538b`     | Write       | `1-5`                                         |
| **Read/Write**        |                                          |             |                                               |
| Mode                  | `1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb`     | R/W         | `1` (ON), `2` (OFF), `3` (SWIM)               |
| Sensitivity (Read)    | `6362168c-c448-44db-b470-793832154859`     | R/W         | `1-5`                                         |
| Standby Time          | `734ecc1d-ed20-4a8c-8eeb-554476154852`     | R/W         | `1-30` (minutes)                              |
| Alarm Length          | `734ecc1d-ed20-4a8c-8eeb-554476188831`     | R/W         | `5-180` (seconds)                             |
| DND To                | `734ecc1d-ed20-4a8c-8eeb-554476364285`     | R/W         | `0-1439` (minutes from midnight)              |
| DND From              | `734ecc1d-ed20-4a8c-8eeb-554476954872`     | R/W         | `0-1439` (minutes from midnight)              |
| DND On/Off            | `e541793c-8a5e-4a5d-b6ff-c6b6c69244a1`     | R/W         | `1` (On), `0` (Off)                           |

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.
