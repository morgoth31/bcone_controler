# bcone_controler

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


configuration 

mode (OFF/ON/swim-mode) (OFF)
reception db (excellent)(-58db)
batterie level (full) (2.947V)


do not disturb (on/off) (set to off)
do not disturb from (hour:minutes) (05:00)
do not disturb to (hour:minutes) (22:00)
stand by time (1-30) (5min)
sensitivity (1-5) (3)
alarm length
version (V1.5.5)
serial number (BCSO2405230693)
storage mode (on/off) (off)
test siren







----------------------------------------

-> Caractéristique: Unknown (f7bf3564-fb6d-4e53-88a4-5e37e0326063)
-> Caractéristique: Unknown (984227f3-34fc-4045-a5d0-2c581f81a153)


??????????????????????????????????????????
-> Caractéristique: Unknown (e541793c-8a5e-4a5d-b6ff-c6b6c69244a1)
  [Read Value]: 00 | ''
  [Notify]: Abonné aux notifications. Écoute des changements...

??????????????????????????????????????????
-> Caractéristique: Unknown (a8c4d597-2e48-4c85-8e36-86e9b694da1d)
  [Read Value]: ff | '�'
  [Notify]: Abonné aux notifications. Écoute des changements...

???????????????????
-> Caractéristique: Unknown (82046727-0625-4196-aed0-f0e661b2eebd)
  [Read Value]: ff | '�'
  [Notify]: Abonné aux notifications. Écoute des changements...

??????????????????????????????
-> Caractéristique: Unknown (1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb)
  [Read Value]: 03 | ''
  [Notify]: Abonné aux notifications. Écoute des changements...

???????????????????????????
-> Caractéristique: Unknown (6362168c-c448-44db-b470-793832a3538b)
  [Read Value]: 02 | ''
  [Notify]: Abonné aux notifications. Écoute des changements...

???????????????????????????????????????????????
-> Caractéristique: Unknown (46c6f78d-dc51-4036-80a9-852824e4125a)
  [Read Value]: ffff | '��'
  [Notify]: Abonné aux notifications. Écoute des changements...

????????????????????????????????????????????
-> Caractéristique: Unknown (734ecc1d-ed20-4a8c-8eeb-554476163524)
  [Read Value]: dc04 | '�'
  [Notify]: Abonné aux notifications. Écoute des changements...











Temperature
-> Caractéristique: Unknown (4d6cbd23-061b-47a2-b82c-cdbaaed98d63)
  [Read Value]: ff00 | '�'
  [Notify]: Abonné aux notifications. Écoute des changements...

stand_by_time
-> Caractéristique: Unknown (734ecc1d-ed20-4a8c-8eeb-554476154852)
  [Read Value]: 05 | ''
  [Notify]: Abonné aux notifications. Écoute des changements...

do_not_disturb_to
-> Caractéristique: Unknown (734ecc1d-ed20-4a8c-8eeb-554476364285)
  [Read Value]: 2805 | '('
  [Notify]: Abonné aux notifications. Écoute des changements...

Batterie_voltage
-> Caractéristique: Unknown (a3768c74-4489-4d82-b557-535f33614e2b)
  [Read Value]: 830b | '�
  [Notify]: Abonné aux notifications. Écoute des changements...

do_not_disturb_from
-> Caractéristique: Unknown (734ecc1d-ed20-4a8c-8eeb-554476954872)
  [Read Value]: 2c01 | ','
  [Notify]: Abonné aux notifications. Écoute des changements...

attenuation
-> Caractéristique: Unknown (9e887463-e6fd-4ff5-a366-6d2f42901a74)
  [Read Value]: c500 | '�'
  [Notify]: Abonné aux notifications. Écoute des changements...

sensibilité
-> Caractéristique: Unknown (6362168c-c448-44db-b470-793832154859)
  [Read Value]: 03 | ''
  [Notify]: Abonné aux notifications. Écoute des changements...


alarm length
-> Caractéristique: Unknown (734ecc1d-ed20-4a8c-8eeb-554476188831)
  [Read Value]: b4 | '�'
  [Notify]: Abonné aux notifications. Écoute des changements...


----------------------------------------
(f7bf3564-fb6d-4e53-88a4-5e37e0326063) ? test siren ?
(984227f3-34fc-4045-a5d0-2c581f81a153) UNKNOWN_WRITE_9842
(e541793c-8a5e-4a5d-b6ff-c6b6c69244a1)
(a8c4d597-2e48-4c85-8e36-86e9b694da1d)
(82046727-0625-4196-aed0-f0e661b2eebd)
(1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb)
(6362168c-c448-44db-b470-793832a3538b)
(46c6f78d-dc51-4036-80a9-852824e4125a)
(734ecc1d-ed20-4a8c-8eeb-554476163524)


CHARACTERISTIC_UUIDS = {
    # Fonctions de contrôle (inscriptibles)
    "MODE": "1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb",
    "SENSITIVITY_WRITE": "6362168c-c448-44db-b470-793832a3538b",
    "STANDBY_TIME": "734ecc1d-ed20-4a8c-8eeb-554476154852",
    "TEST_SIREN": "f7bf3564-fb6d-4e53-88a4-5e37e0326063",
    "ALARM_LENGTH": "734ecc1d-ed20-4a8c-8eeb-554476188831",
    "DO_NOT_DISTURB_TO": "734ecc1d-ed20-4a8c-8eeb-554476364285",
    "DO_NOT_DISTURB_FROM": "734ecc1d-ed20-4a8c-8eeb-554476954872",
    "DO_NOT_DISTURB_ON_OFF": "e541793c-8a5e-4a5d-b6ff-c6b6c69244a1",
    "UNKNOWN_WRITE_9842": "984227f3-34fc-4045-a5d0-2c581f81a153",
    
    # Données des capteurs et informations (lecture seule)
    "SENSITIVITY_READ": "6362168c-c448-44db-b470-793832154859",
    "BATTERY_LEVEL": "a3768c74-4489-4d82-b557-535f33614e2b",
    "SIGNAL_ATTENUATION": "9e887463-e6fd-4ff5-a366-6d2f42901a74",
    "TEMPERATURE": "4d6cbd23-061b-47a2-b82c-cdbaaed98d63",
    "MANUFACTURER_NAME": "00002a29-0000-1000-8000-00805f9b34fb",
    "MODEL_NUMBER": "00002a24-0000-1000-8000-00805f9b34fb",
    "SYSTEM_ID": "00002a23-0000-1000-8000-00805f9b34fb",
    "DATABASE_HASH": "00002b2a-0000-1000-8000-00805f9b34fb",
    "ALARM_STATUS": "82046727-0625-4196-aed0-f0e661b2eebd",
    
    "UNKNOWN_734E": "734ecc1d-ed20-4a8c-8eeb-554476163524",

    # UUIDs à surveiller
    "UNKNOWN_A8C4": "a8c4d597-2e48-4c85-8e36-86e9b694da1d",
    "UNKNOWN_46C6": "46c6f78d-dc51-4036-80a9-852824e4125a",

    
}













-> Caractéristique: Unknown (f7bf3564-fb6d-4e53-88a4-5e37e0326063)
-> Caractéristique: Unknown (984227f3-34fc-4045-a5d0-2c581f81a153)

-> Caractéristique: Unknown (e541793c-8a5e-4a5d-b6ff-c6b6c69244a1) 
00

-> Caractéristique: Unknown (a8c4d597-2e48-4c85-8e36-86e9b694da1d)
FF
???????????????????
-> Caractéristique: Unknown (82046727-0625-4196-aed0-f0e661b2eebd)...
00
??????????????????????????????
-> Caractéristique: Unknown (1c9fa3f2-6dd2-4437-a1f9-4b3d76adddfb)
3
???????????????????????????
-> Caractéristique: Unknown (6362168c-c448-44db-b470-793832a3538b)
3

???????????????????????????????????????????????
-> Caractéristique: Unknown (46c6f78d-dc51-4036-80a9-852824e4125a)
FFFF

mode
-> Caractéristique: Unknown (734ecc1d-ed20-4a8c-8eeb-554476163524)
3900
5900

6200 storage
7500 swim mode
7F00 ON
8600 OFF

8a00 off, do not disturb



storage, swim/on/off, 






->  sensibility (6362168c-c448-44db-b470-793832154859) 03
->  stand_by_time (734ecc1d-ed20-4a8c-8eeb-554476154852) 05
->  signal_attenuation_in_db (9e887463-e6fd-4ff5-a366-6d2f42901a74)
->  alarm_length (734ecc1d-ed20-4a8c-8eeb-554476188831)
->  do_not_disturb_to (734ecc1d-ed20-4a8c-8eeb-554476364285)
->  do_not_disturb_from (734ecc1d-ed20-4a8c-8eeb-554476954872)
->  Batterie_voltage (a3768c74-4489-4d82-b557-535f33614e2b)
->  Temperature (4d6cbd23-061b-47a2-b82c-cdbaaed98d63)
->  Database Hash (00002b2a-0000-1000-8000-00805f9b34fb)
->  Service Changed (00002a05-0000-1000-8000-00805f9b34fb)
->  Client Supported Features (00002b29-0000-1000-8000-00805f9b34fb)
->  Manufacturer Name String (00002a29-0000-1000-8000-00805f9b34fb)
->  Model Number String (00002a24-0000-1000-8000-00805f9b34fb)
->  System ID (00002a23-0000-1000-8000-00805f9b34fb)
