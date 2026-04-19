from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import hashlib
import base64
import numpy as np

import json
import os

class QuantumSimulator:
    def __init__(self):
        # Persistent Key Vault
        self.vault_file = "key_vault.json"
        self.key_vault = self._load_vault()

    def _load_vault(self):
        if os.path.exists(self.vault_file):
            try:
                with open(self.vault_file, "r") as f:
                    data = json.load(f)
                    # Convert hex strings back to bytes if needed, but we store as hex/b64 usually
                    # For simplicity, we'll store bytes as hex strings in JSON
                    return data
            except:
                return {}
        return {}

    def _save_vault(self):
        with open(self.vault_file, "w") as f:
            json.dump(self.key_vault, f, indent=4)

    def generate_key(self, length=256):
        """
        Simulates QKD by generating random bits using Quantum Circuit measurements.
        Uses Statevector for compatibility across Qiskit versions.
        """
        num_qubits = 16
        raw_bits = ""
        
        while len(raw_bits) < length:
            qc = QuantumCircuit(num_qubits)
            # Apply Hadamard to all qubits to put them in superposition
            qc.h(range(num_qubits))
            
            # Use Statevector to get the probabilities and sample from them
            state = Statevector.from_instruction(qc)
            probs = state.probabilities_dict()
            
            # Sample a state based on the probabilities
            # In a uniform superposition, all states are equally likely
            states = list(probs.keys())
            probabilities = list(probs.values())
            
            # Use numpy to sample based on distribution
            sampled_state = np.random.choice(states, p=probabilities)
            # sampled_state is a binary string like '1010...'
            raw_bits += sampled_state
                
        # Trim to length
        raw_bits = raw_bits[:length]
        
        # Convert binary string to bytes
        key_int = int(raw_bits, 2)
        # Ensure we handle the conversion to 32 bytes (256 bits) correctly
        key_bytes = key_int.to_bytes(32, byteorder='big')
        
        # Hash it to ensure uniform distribution
        final_key = hashlib.sha256(key_bytes).digest()
        
        # Store in vault with a unique ID
        # Store as HEX string for JSON compatibility
        qkd_id = hashlib.md5(final_key).hexdigest()[:8]
        self.key_vault[qkd_id] = final_key.hex()
        self._save_vault()
        
        return final_key, base64.b64encode(final_key).decode('utf-8'), qkd_id

    def get_key_from_vault(self, qkd_id):
        """Simulates fetching a key from the KM via API"""
        hex_key = self.key_vault.get(qkd_id)
        if hex_key:
            return bytes.fromhex(hex_key)
        return None

if __name__ == "__main__":
    qs = QuantumSimulator()
    k_bytes, k_str, q_id = qs.generate_key()
    print(f"ID: {q_id} | Key: {k_str}")
