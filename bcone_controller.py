import asyncio
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError

async def main():
    """
    Fonction principale pour scanner, connecter et lister les services d'un appareil BLE.
    """
    print("--- Explorateur de Services Bluetooth Low Energy ---")
    
    # --- Étape 1: Scanner les appareils à proximité ---
    print("\nScanning for BLE devices for 10 seconds...")
    try:
        devices = await BleakScanner.discover(timeout=10.0)
    except BleakError as e:
        print(f"Erreur lors du scan : {e}")
        print("Assurez-vous que votre adaptateur Bluetooth est activé.")
        return

    if not devices:
        print("Aucun appareil BLE trouvé à proximité. Assurez-vous que votre appareil est allumé et en mode d'appairage.")
        return

    # --- Étape 2: Afficher les appareils et laisser l'utilisateur choisir ---
    print("\nAppareils trouvés :")
    device_list = list(devices)
    for i, device in enumerate(device_list):
        # Affiche le nom s'il est disponible, sinon "Unknown"
        device_name = device.name or "Unknown"
        print(f"  {i}: {device.address} - {device_name}")

    try:
        choice = int(input("\nEntrez le numéro de l'appareil auquel vous connecter : "))
        if not 0 <= choice < len(device_list):
            print("Choix invalide.")
            return
        target_device = device_list[choice]
    except (ValueError, IndexError):
        print("Entrée invalide. Veuillez entrer un numéro de la liste.")
        return

    # --- Étape 3: Se connecter à l'appareil choisi et lister les services ---
    address = target_device.address
    print(f"\nTentative de connexion à {address}...")

    try:
        async with BleakClient(address, timeout=20.0) as client:
            if client.is_connected:
                print(f"✅ Connecté avec succès à {target_device.name or address}!")
                
                print("\n--- Fonctions (Services et Caractéristiques) ---")
                # Itérer à travers tous les services de l'appareil
                for service in client.services:
                    print(f"\n[Service] UUID: {service.uuid}")
                    print(f"          Description: {service.description or 'N/A'}")
                    
                    # Pour chaque service, itérer à travers ses caractéristiques
                    for char in service.characteristics:
                        properties = ", ".join(char.properties)
                        print(f"  -> [Caractéristique] UUID: {char.uuid}")
                        print(f"                     Description: {char.description or 'N/A'}")
                        print(f"                     Propriétés: {properties}") # (read, write, notify, etc.)

            else:
                print(f"❌ Échec de la connexion à {address}.")

    except BleakError as e:
        print(f"Erreur de connexion ou de communication : {e}")
    except asyncio.TimeoutError:
        print(f"Timeout : La connexion à {address} a pris trop de temps.")


if __name__ == "__main__":
    # Lancer le programme principal de manière asynchrone
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")

