import os, json, base64, hashlib, platform
from cryptography.fernet import Fernet
from typing import Any, Dict
from pathlib import Path

class EncryptedJSONStorage:
    def __init__(self, filename: str, directory: str = None):
        """Initialize the encrypted storage object with a directory.

        Args:
            filename (str): Name of the JSON file to store data.
            directory (str, optional): Directory to store the JSON file. Defaults to ~/.junior.
        """
        if directory is None:
            # Default to ~/.junior directory
            directory = os.path.join(Path.home(), ".junior")
        else:
            directory = Path(directory)

        # Ensure the storage directory exists
        os.makedirs(directory, exist_ok=True)

        # Path to the JSON file
        self.filepath = os.path.join(directory, filename)

        # Use the machine-specific key
        #print(f"Machine ID: {self._get_machine_id()}")
        self.cipher = Fernet(self._generate_machine_key())

    def _get_machine_id(self) -> str:
        """Retrieve a unique machine identifier."""
        system = platform.system()

        if system == "Windows":
            # Use the disk serial number
            output = os.popen('wmic diskdrive get SerialNumber').read()
            serial_number = output.splitlines()[1].strip()
            return serial_number
        elif system == "Darwin":
            # Use the macOS serial number
            output = os.popen('system_profiler SPHardwareDataType').read()
            for line in output.splitlines():
                if "Serial Number" in line:
                    return line.split(":")[-1].strip()
        elif system == "Linux":
            # Use the product UUID or disk serial number
            uuid_path = '/sys/class/dmi/id/product_uuid'
            if os.path.exists(uuid_path):
                with open(uuid_path, 'r') as file:
                    return file.read().strip()
            else:
                output = os.popen('lsblk -o SERIAL').read()
                serial_number = output.splitlines()[1].strip()
                return serial_number

        return "fallback-unique-id"  # Fallback identifier if none is found

    def _generate_machine_key(self) -> bytes:
        """Generate a machine-specific Fernet key based on hardware info."""
        machine_id = self._get_machine_id()
        hashed_id = hashlib.sha256(machine_id.encode()).digest()
        return base64.urlsafe_b64encode(hashed_id[:32])

    def encrypt_value(self, value: Any) -> Any:
        """Encrypts a value.

        Args:
            value (Any): The value to encrypt.

        Returns:
            Any: The encrypted value.
        """
        if isinstance(value, dict):
            return {k: self.encrypt_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.encrypt_value(item) for item in value]
        else:
            value = json.dumps(value)
            return self.cipher.encrypt(value.encode()).decode()

    def decrypt_value(self, value: Any) -> Any:
        """Decrypts a value.

        Args:
            value (Any): The value to decrypt.

        Returns:
            Any: The decrypted value.
        """
        if isinstance(value, dict):
            return {k: self.decrypt_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.decrypt_value(item) for item in value]
        else:
            return json.loads(self.cipher.decrypt(value.encode()).decode())

    def save(self, data: Dict):
        """Encrypts and saves the data to a JSON file.

        Args:
            data (Dict): The data to save.
        """
        encrypted_data = self.encrypt_value(data)
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(encrypted_data, file, indent=4)

    def load(self) -> Dict:
        """Loads and decrypts the data from a JSON file.

        Returns:
            Dict: The decrypted data.
        """
        if not os.path.exists(self.filepath):
            return {}  # Return empty dict if the file does not exist

        with open(self.filepath, 'r', encoding='utf-8') as file:
            encrypted_data = json.load(file)
            return self.decrypt_value(encrypted_data)

    def set(self, key: str, value: Any):
        """Sets a key-value pair in the encrypted storage.

        Args:
            key (str): The key to set.
            value (Any): The value to associate with the key.
        """
        data = self.load()
        data[key] = value
        self.save(data)

    def get(self, key: str) -> Any:
        """Gets the value associated with a given key.

        Args:
            key (str): The key to retrieve the value.

        Returns:
            Any: The value if present, else None.
        """
        data = self.load()
        return data.get(key)

    def delete(self, key: str):
        """Deletes a key-value pair from the storage.

        Args:
            key (str): The key to delete.
        """
        data = self.load()
        if key in data:
            del data[key]
            self.save(data)

    def clear(self):
        """Clear all storage entries."""
        self.save({})

# Usage Example
if __name__ == "__main__":
    # Initialize the encrypted storage with a custom directory
    storage = EncryptedJSONStorage('encrypted_data.json', directory=".")

    # Store some data
    storage.set("example", {"data": "test"})

    # Retrieve the stored data
    value = storage.get("example")
    print(f"Stored Value: {value}")

    # Delete the stored data
    storage.delete("example")

    # Clear all storage
    storage.clear()
