# utils.py
from cryptography.fernet import Fernet
import base64
import json
from django.conf import settings

# Generate a key from the SECRET_KEY
SECRET_KEY = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32])

def encrypt(data):
    fernet = Fernet(SECRET_KEY)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt(token):
    fernet = Fernet(SECRET_KEY)
    decrypted_data = fernet.decrypt(token.encode())
    return decrypted_data.decode()