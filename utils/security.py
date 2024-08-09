from cryptography.fernet import Fernet
import os
import logging
import cryptography

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_or_generate_key():
    if not os.path.exists('secret.key'):
        key = Fernet.generate_key()
        with open('secret.key', 'wb') as key_file:
            key_file.write(key)
        logging.debug("Generated new encryption key.")
    else:
        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
        logging.debug("Loaded existing encryption key.")
    return key

key = load_or_generate_key()
cipher = Fernet(key)

def encrypt_data(data):
    encrypted = cipher.encrypt(data.encode())
    logging.debug(f"Data encrypted successfully: {encrypted[:50]}...")
    return encrypted

def decrypt_data(encrypted_data):
    try:
        decrypted = cipher.decrypt(encrypted_data).decode()
        logging.debug(f"Data decrypted successfully: {decrypted[:50]}...")
        return decrypted
    except cryptography.fernet.InvalidToken:
        logging.error("Failed to decrypt data. The data may be corrupted or the key may be incorrect.")
        raise ValueError("Failed to decrypt data. The data may be corrupted or the key may be incorrect.")
