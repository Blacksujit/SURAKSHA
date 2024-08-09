from cryptography.fernet import Fernet

# Define your key
key = b'avDXLjYY9toO8H3TSDPKCfE5nFZa0l7QjsKRqIKYHc0='

# Initialize Fernet cipher
cipher = Fernet(key)

# Test encryption and decryption
def test_encryption_decryption():
    original_data = "Test data"
    encrypted_data = cipher.encrypt(original_data.encode())
    print(f"Encrypted data: {encrypted_data}")

    try:
        decrypted_data = cipher.decrypt(encrypted_data).decode()
        print(f"Decrypted data: {decrypted_data}")
    except Exception as e:
        print(f"Error during decryption: {e}")

test_encryption_decryption()
