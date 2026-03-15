from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.VAULT_ENCRYPTION_KEY)

def encrypt_file(file_bytes):
    return fernet.encrypt(file_bytes)

def decrypt_file(file_bytes):
    return fernet.decrypt(file_bytes)