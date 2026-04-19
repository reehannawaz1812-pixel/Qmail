import base64
import requests
import json
import os
from crypto.aes import encrypt as aes_encrypt, decrypt as aes_decrypt
from crypto.crystal.kyber import Kyber512
import crypto.crypto as pqc_crypto

class SecurityEngine:
    def __init__(self, km_host, local_sae_id):
        self.km_host = km_host  # e.g., "127.0.0.1:8000"
        self.local_sae_id = local_sae_id

    def _xor_bytes(self, data, key):
        return bytes(a ^ b for a, b in zip(data, key))

    def _get_qkd_key_enc(self, target_sae_id):
        url = f"http://{self.km_host}/quantserver/api/v1/keys/{target_sae_id}/enc_keys?source_ID={self.local_sae_id}"
        response = requests.get(url).json()
        key_id = response['keys'][0]['key_ID']
        key_val = base64.b64decode(response['keys'][0]['key'])
        return key_id, key_val

    def _get_qkd_key_dec(self, source_sae_id, key_id):
        url = f"http://{self.km_host}/quantserver/api/v1/keys/{source_sae_id}/dec_keys?key_ID={key_id}"
        response = requests.get(url).json()
        key_val = base64.b64decode(response['keys'][0]['key'])
        return key_val

    def encrypt_message(self, message, receiver_id, level, receiver_public_key=None):
        """
        level 1: OTP (Quantum Secure)
        level 2: Quantum-aided AES
        level 3: PQC (Kyber)
        level 4: Plain (No Quantum)
        """
        if level == 1:
            # OTP requires key same length as message. 
            # For simulation, we'll fetch a 256-bit key and repeat it if needed, 
            # or just assume message < 256 bits.
            key_id, key_val = self._get_qkd_key_enc(receiver_id)
            msg_bytes = message.encode('utf-8')
            # In real OTP, we'd request exact length from KM.
            padded_key = (key_val * (len(msg_bytes) // len(key_val) + 1))[:len(msg_bytes)]
            encrypted = self._xor_bytes(msg_bytes, padded_key)
            payload = {
                "level": 1,
                "key_id": key_id,
                "data": base64.b64encode(encrypted).decode('utf-8')
            }
            return json.dumps(payload)

        elif level == 2:
            key_id, key_val = self._get_qkd_key_enc(receiver_id)
            # Use QKD key as seed for AES
            passkey = base64.b64encode(key_val).decode('utf-8')
            encrypted_data = aes_encrypt(message, passkey)
            payload = {
                "level": 2,
                "key_id": key_id,
                "data": encrypted_data
            }
            return json.dumps(payload)

        elif level == 3:
            # Existing PQC implementation
            encrypted = pqc_crypto.encrypt(message, receiver_public_key)
            payload = {
                "level": 3,
                "data": encrypted
            }
            return json.dumps(payload)

        else:
            return message

    def decrypt_message(self, encrypted_payload, sender_id, username=None):
        try:
            payload = json.loads(encrypted_payload)
        except:
            return encrypted_payload # Probably level 4 or plain text

        level = payload.get("level")
        
        if level == 1:
            key_id = payload["key_id"]
            key_val = self._get_qkd_key_dec(sender_id, key_id)
            encrypted_data = base64.b64decode(payload["data"])
            padded_key = (key_val * (len(encrypted_data) // len(key_val) + 1))[:len(encrypted_data)]
            decrypted = self._xor_bytes(encrypted_data, padded_key)
            return decrypted.decode('utf-8')

        elif level == 2:
            key_id = payload["key_id"]
            key_val = self._get_qkd_key_dec(sender_id, key_id)
            passkey = base64.b64encode(key_val).decode('utf-8')
            decrypted = aes_decrypt(payload["data"], passkey)
            return decrypted.decode('utf-8')

        elif level == 3:
            # Existing PQC implementation
            # Note: pqc_crypto.decrypt requires tag and concatenated_string
            data = payload["data"]
            return pqc_crypto.decrypt(data["tag"], data["concatenated_string"], username)

        return encrypted_payload
