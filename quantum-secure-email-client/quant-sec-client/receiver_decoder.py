import base64
import hashlib
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

# Optional: Import existing Kyber if available in the project
try:
    from crypto.crystal.kyber import Kyber512
    KYBER_AVAILABLE = True
except ImportError:
    KYBER_AVAILABLE = False

class ReceiverDecoder:
    """
    A module to handle the receiver-side decoding of secure emails.
    Includes signature verification, asymmetric decryption of the symmetric key,
    and symmetric decryption of the email content.
    """

    @staticmethod
    def verify_signature(data, signature, sender_public_key_pem):
        """
        Step 2a: Verify the digital signature using the sender’s public key.
        """
        try:
            public_key = RSA.import_key(sender_public_key_pem)
            # Create a hash of the data to verify against the signature
            h = SHA256.new(data.encode('utf-8') if isinstance(data, str) else data)
            pkcs1_15.new(public_key).verify(h, base64.b64decode(signature))
            print("[INFO] Digital signature verified successfully.")
            return True
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Signature verification failed: {e}")
            return False

    @staticmethod
    def decrypt_symmetric_key(encrypted_key_b64, receiver_private_key_pem):
        """
        Step 2b: Decrypt the symmetric key using the receiver’s private key (RSA).
        """
        try:
            private_key = RSA.import_key(receiver_private_key_pem)
            cipher_rsa = PKCS1_OAEP.new(private_key)
            encrypted_key = base64.b64decode(encrypted_key_b64)
            symmetric_key = cipher_rsa.decrypt(encrypted_key)
            print("[INFO] Symmetric key decrypted successfully.")
            return symmetric_key
        except Exception as e:
            print(f"[ERROR] Failed to decrypt symmetric key: {e}")
            return None

    @staticmethod
    def decrypt_content(encrypted_content_b64, symmetric_key, iv_b64):
        """
        Step 2c: Use the decrypted symmetric key to decrypt the email content (AES-256).
        """
        try:
            encrypted_content = base64.b64decode(encrypted_content_b64)
            iv = base64.b64decode(iv_b64)
            
            # AES-256 in CBC mode (standard for secure messaging)
            cipher_aes = AES.new(symmetric_key, AES.MODE_CBC, iv)
            decrypted_padded = cipher_aes.decrypt(encrypted_content)
            
            # Remove padding
            decrypted_text = unpad(decrypted_padded, AES.block_size).decode('utf-8')
            print("[INFO] Message content decrypted successfully.")
            return decrypted_text
        except Exception as e:
            print(f"[ERROR] Failed to decrypt content: {e}")
            return None

    @staticmethod
    def validate_integrity(decrypted_text, original_hash_hex):
        """
        Step 2d: Validate message integrity using SHA-256 hash comparison.
        """
        try:
            current_hash = hashlib.sha256(decrypted_text.encode('utf-8')).hexdigest()
            if current_hash == original_hash_hex:
                print("[INFO] Integrity check passed: Hash matches.")
                return True
            else:
                print("[ERROR] Integrity check failed: Hash mismatch!")
                return False
        except Exception as e:
            print(f"[ERROR] Integrity validation error: {e}")
            return False

    def decode_email(self, encrypted_payload, sender_public_key, receiver_private_key):
        """
        Full decoding flow as requested.
        """
        print("\n--- Starting Decoding Flow ---")
        
        # 1. Extract data from payload
        data = encrypted_payload.get('data')
        signature = encrypted_payload.get('signature')
        encrypted_key = encrypted_payload.get('encrypted_key')
        iv = encrypted_payload.get('iv')
        expected_hash = encrypted_payload.get('hash')

        # 2a. Verify Signature
        # We verify the signature over the encrypted data + encrypted key to ensure authenticity of the whole package
        payload_to_verify = f"{data}{encrypted_key}{iv}"
        if not self.verify_signature(payload_to_verify, signature, sender_public_key):
            return "Error: Authentication Failure (Invalid Signature)"

        # 2b. Decrypt Symmetric Key
        symmetric_key = self.decrypt_symmetric_key(encrypted_key, receiver_private_key)
        if not symmetric_key:
            return "Error: Decryption Failure (Key Decryption Error)"

        # 2c. Decrypt Content
        plaintext = self.decrypt_content(data, symmetric_key, iv)
        if not plaintext:
            return "Error: Decryption Failure (Content Decryption Error)"

        # 2d. Validate Integrity
        if not self.validate_integrity(plaintext, expected_hash):
            return "Error: Integrity Failure (Message may have been tampered with)"

        print("--- Decoding Flow Completed Successfully ---\n")
        return plaintext

# --- Post-Quantum Extension (Optional) ---
class PQCReceiverDecoder(ReceiverDecoder):
    """
    Extends ReceiverDecoder with Kyber support.
    """
    @staticmethod
    def decrypt_symmetric_key_kyber(encrypted_key_b64, kyber_private_key_b64):
        if not KYBER_AVAILABLE:
            return "Error: Kyber library not found."
        
        try:
            ciphertext = base64.b64decode(encrypted_key_b64)
            private_key = base64.b64decode(kyber_private_key_b64)
            shared_secret = Kyber512.dec(ciphertext, private_key)
            print("[INFO] Kyber shared secret decrypted successfully.")
            return shared_secret
        except Exception as e:
            print(f"[ERROR] Kyber decryption failed: {e}")
            return None

def run_example():
    """
    Example test case with sample data.
    In a real scenario, these would be received over the network.
    """
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Util.Padding import pad

    print("Generating sample keys and data...")
    # Generate RSA keys for Receiver
    receiver_key = RSA.generate(2048)
    receiver_private_pem = receiver_key.export_key().decode('utf-8')
    receiver_public_pem = receiver_key.publickey().export_key().decode('utf-8')

    # Generate RSA keys for Sender
    sender_key = RSA.generate(2048)
    sender_public_pem = sender_key.publickey().export_key().decode('utf-8')
    sender_private_pem = sender_key.export_key().decode('utf-8')

    # Original Message
    original_message = "This is a highly secure quantum-resistant email message."
    print(f"Original Message: {original_message}")

    # --- SENDER SIDE SIMULATION ---
    # 1. Create Symmetric Key (AES-256)
    symmetric_key = get_random_bytes(32) # 256 bits
    iv = get_random_bytes(16)
    
    # 2. Encrypt Message
    cipher_aes = AES.new(symmetric_key, AES.MODE_CBC, iv)
    encrypted_msg = cipher_aes.encrypt(pad(original_message.encode('utf-8'), AES.block_size))
    encrypted_msg_b64 = base64.b64encode(encrypted_msg).decode('utf-8')
    iv_b64 = base64.b64encode(iv).decode('utf-8')

    # 3. Encrypt Symmetric Key with Receiver's Public Key
    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(receiver_public_pem))
    encrypted_key = cipher_rsa.encrypt(symmetric_key)
    encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')

    # 4. Create Hash for Integrity
    msg_hash = hashlib.sha256(original_message.encode('utf-8')).hexdigest()

    # 5. Sign the payload (Sender's Private Key)
    payload_to_sign = f"{encrypted_msg_b64}{encrypted_key_b64}{iv_b64}"
    h = SHA256.new(payload_to_sign.encode('utf-8'))
    signature = pkcs1_15.new(RSA.import_key(sender_private_pem)).sign(h)
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    # Constructed Payload
    payload = {
        'data': encrypted_msg_b64,
        'signature': signature_b64,
        'encrypted_key': encrypted_key_b64,
        'iv': iv_b64,
        'hash': msg_hash
    }

    # --- RECEIVER SIDE ---
    decoder = ReceiverDecoder()
    decrypted_text = decoder.decode_email(payload, sender_public_pem, receiver_private_pem)

    print(f"Decoded Result: {decrypted_text}")

    if KYBER_AVAILABLE:
        print("\n--- Testing Post-Quantum (Kyber) Flow ---")
        # 1. Generate Kyber Keys
        pk, sk = Kyber512.keygen()
        pk_b64 = base64.b64encode(pk).decode('utf-8')
        sk_b64 = base64.b64encode(sk).decode('utf-8')

        # 2. Sender: Encapsulate (Encrypt) a shared secret
        c, shared_secret_sender = Kyber512.enc(pk)
        c_b64 = base64.b64encode(c).decode('utf-8')

        # 3. Receiver: Decapsulate (Decrypt) the shared secret
        pqc_decoder = PQCReceiverDecoder()
        shared_secret_receiver = pqc_decoder.decrypt_symmetric_key_kyber(c_b64, sk_b64)

        if shared_secret_sender == shared_secret_receiver:
            print("[SUCCESS] Kyber Post-Quantum key exchange successful!")
            print(f"Shared Secret (first 16 bytes hex): {shared_secret_receiver[:16].hex()}...")
        else:
            print("[FAILURE] Kyber Post-Quantum key exchange failed.")

if __name__ == "__main__":
    run_example()
