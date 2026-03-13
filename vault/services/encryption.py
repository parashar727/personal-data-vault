import json
from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.VAULT_ENCRYPTION_KEY)

def encrypt_data(data: dict) -> str:
    """
    Encrypt input dictionary and return encrypted string sequence
    """
    json_string = json.dumps(data)
    encrypted_data = fernet.encrypt(json_string.encode())
    return encrypted_data.decode()

def decrypt_data(ciphertext: str) -> dict:
    """
    Decrypt encrypted string sequence in database and return dicttionary
    """
    decrypted_data = fernet.decrypt(ciphertext.encode())
    return json.loads(decrypted_data.decode())
