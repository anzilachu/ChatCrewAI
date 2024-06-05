# utils.py
import json
from cryptography.fernet import Fernet
import base64
from django.conf import settings

def get_fernet_key():
    secret_key = settings.SECRET_KEY
    if len(secret_key) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long")
    return base64.urlsafe_b64encode(secret_key.encode()[:32])

key = get_fernet_key()
fernet = Fernet(key)

import logging

logger = logging.getLogger(__name__)

def encrypt(text):
    if text is None:
        return None
    encrypted = base64.urlsafe_b64encode(fernet.encrypt(text.encode())).decode()
    logger.debug(f"Encrypting '{text}' to '{encrypted}'")
    return encrypted

def decrypt(token):
    if token is None:
        return None
    decrypted = fernet.decrypt(base64.urlsafe_b64decode(token)).decode()
    logger.debug(f"Decrypting '{token}' to '{decrypted}'")
    return decrypted


def encrypt_params(params):
    encrypted = encrypt(json.dumps(params))
    return encrypted

def decrypt_params(encrypted_params):
    decrypted = decrypt(encrypted_params)
    return json.loads(decrypted)

import razorpay
from django.conf import settings

def get_razorpay_client():
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    return client

def get_converted_amount(amount, currency):
    conversion_rates = {
        'USD': 1,  # No conversion needed as we are charging in USD
        'EUR': 1.2,  # Example rate; you might need to update this
    }
    return int(amount * conversion_rates.get(currency, 1))
