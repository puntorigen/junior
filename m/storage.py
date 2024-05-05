import json
import os
from cryptography.fernet import Fernet
from typing import Any, Dict

class EncryptedJSONStorage:
    def __init__(self, filename: str, key: bytes = None):
        self.filepath = os.path.join(os.path.expanduser('~'), filename)
        self.key = key if key else Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_value(self, value: Any) -> str:
        """
        Encrypts a value.
        """
        if isinstance(value, dict):
            return {k: self.encrypt_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.encrypt_value(item) for item in value]
        else:
            value = json.dumps(value)
            return self.cipher.encrypt(value.encode()).decode()

    def decrypt_value(self, value: Any) -> Any:
        """
        Decrypts a value.
        """
        if isinstance(value, dict):
            return {k: self.decrypt_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.decrypt_value(item) for item in value]
        else:
            return json.loads(self.cipher.decrypt(value.encode()).decode())

    def save(self, data: Dict):
        """
        Encrypts and saves the data to a JSON file.
        """
        encrypted_data = self.encrypt_value(data)
        with open(self.filepath, 'w') as file:
            json.dump(encrypted_data, file, indent=4)

    def load(self) -> Dict:
        """
        Loads and decrypts the data from a JSON file.
        """
        if not os.path.exists(self.filepath):
            return {}  # Return empty dict if the file does not exist

        with open(self.filepath, 'r') as file:
            encrypted_data = json.load(file)
            return self.decrypt_value(encrypted_data)

# Usage example:
#storage = EncryptedJSONStorage('encrypted_data.json')
#data = {'name': 'John Doe', 'age': 30, 'children': [{'name': 'Jane Doe', 'age': 10}]}
#storage.save(data)

#loaded_data = storage.load()
#print(loaded_data)
