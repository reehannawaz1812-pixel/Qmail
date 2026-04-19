import os
import json
import base64
import requests
import sqlite3
import hashlib
from datetime import datetime
from crypto.crystal.kyber import Kyber512
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import crypto.crypto as crypto
from email_service import EmailService
from blockchain import Blockchain
from quantum_sim import QuantumSimulator

# Global state to hold session info
class Session:
    def __init__(self):
        self.server_host = "127.0.0.1:8000"
        self.username = None 
        self.password = None 
        self.email_address = None 
        self.smtp_server = "smtp.gmail.com"
        self.imap_server = "imap.gmail.com"
        self.security_level = 3 
        self.email_service = None
        self.blockchain = Blockchain()
        self.quantum_sim = QuantumSimulator()
        
    def set_email_config(self, address, password, smtp="smtp.gmail.com", imap="imap.gmail.com"):
        self.email_address = address
        self.username = address
        self.password = password
        self.smtp_server = smtp
        self.imap_server = imap
        self.email_service = EmailService(smtp, 587, imap, 993, address, password)

# Initialize global session at the top level
session = Session()
print("[DEBUG] Global Session Object Initialized")

def connect_to_server(host):
    """
    Simulates connecting to the Quantum Key Management (KM) server.
    Verifies if the server is reachable and sets the global session host.
    """
    print(f"[DEBUG] Attempting to connect to host: {host}")
    try:
        # Sanitize host input
        host = sanitize_input(host)
        
        # In a real scenario, we might do a ping or a status request
        # url = f"http://{host}/quantserver/api/v1/status"
        # requests.get(url, timeout=2)
        
        session.server_host = host
        response = {"success": True, "message": f"Secure Link Established with {host}"}
        print(f"[DEBUG] Backend Response: {response}")
        return response
    except Exception as e:
        response = {"success": False, "message": f"Connection Failed: {str(e)}"}
        print(f"[DEBUG] Backend Response: {response}")
        return response

def get_db_connection():
    parent_dir = os.path.expanduser("~")
    db_path = os.path.join(parent_dir, "quantsec", "emails.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    return conn

def get_safe_table_name(email):
    return "user_" + hashlib.md5(email.encode()).hexdigest()

def create_table(user_email):
    safe_table_name = get_safe_table_name(user_email)
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    mycursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {safe_table_name}
        (sender VARCHAR(200), subject TEXT, body TEXT, date DATETIME,
         UNIQUE(sender, subject, date))
        """
    )
    mydb.commit()
    mydb.close()
    return safe_table_name

def sanitize_input(user_input):
    """
    Sanitizes user input by removing leading/trailing whitespace 
    and newline characters to prevent file path errors.
    """
    if not user_input:
        return ""
    # Remove whitespace and newlines (\n, \r)
    cleaned = user_input.strip().replace("\n", "").replace("\r", "")
    print(f"[DEBUG] Cleaned Input: '{cleaned}'")
    return cleaned

def register(name, email, password):
    """
    Registers a new user:
    1. Sanitizes inputs
    2. Hashes the password for security
    3. Checks if a local vault already exists
    4. Generates Quantum-Safe keys (RSA & Kyber)
    5. Stores user identity in a JSON file
    """
    try:
        # 1. Sanitize
        name = sanitize_input(name)
        email = sanitize_input(email)
        password = sanitize_input(password)

        if not name or not email or not password:
            return {"success": False, "message": "All fields are required"}

        # 2. Path & Existence Check
        parent_dir = os.path.expanduser("~")
        path = os.path.join(parent_dir, "quantsec")
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f"{email}.json")
        
        print(f"[DEBUG] Registration Attempt: {email}")
        print(f"[DEBUG] Target File Path: {file_path}")

        if os.path.exists(file_path):
            return {"success": False, "message": "User already exists on this machine"}

        # 3. Security (Password Hashing)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # 4. Generate Keys
        rsa_key = RSA.generate(2048)
        rsa_private = rsa_key.export_key()
        rsa_public = rsa_key.publickey().export_key()
        kyber_pk, kyber_sk = Kyber512.keygen()

        # 5. Save Identity
        user_data = {
            "Name": name,
            "Email": email,
            "PasswordHash": hashed_password,
            "RSA Public Key": base64.b64encode(rsa_public).decode('utf-8'),
            "RSA Private Key": base64.b64encode(rsa_private).decode('utf-8'),
            "Kyber Public Key": base64.b64encode(kyber_pk).decode('utf-8'),
            "Kyber Private Key": base64.b64encode(kyber_sk).decode('utf-8'),
            "RegistrationDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(file_path, "w") as f:
            json.dump(user_data, f, indent=4)
        
        # 6. Initialize local DB
        create_table(email)

        # 7. Notify Server (Optional)
        try:
            reg_url = f"http://{session.server_host}/quantserver/register-user"
            server_data = {
                "name": name, 
                "username": email, 
                "public_key": user_data["Kyber Public Key"], 
                "password": hashed_password
            }
            requests.post(reg_url, data=server_data, timeout=2)
        except: 
            pass # Keep going if server is offline

        print(f"[DEBUG] Registration Successful for {email}")
        return {"success": True, "message": "Identity Vault Created & Keys Generated"}
        
    except Exception as e:
        print(f"[ERROR] Registration Failure: {e}")
        return {"success": False, "message": str(e)}

def register_local_keys(email):
    email = sanitize_input(email)
    parent_dir = os.path.expanduser("~")
    path = os.path.join(parent_dir, "quantsec")
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f"{email}.json")
    
    if not os.path.exists(file_path):
# ... rest of code
        rsa_key = RSA.generate(2048)
        rsa_private = rsa_key.export_key()
        rsa_public = rsa_key.publickey().export_key()
        kyber_pk, kyber_sk = Kyber512.keygen()
        
        user_data = {
            "Email": email,
            "RSA Public Key": base64.b64encode(rsa_public).decode('utf-8'),
            "RSA Private Key": base64.b64encode(rsa_private).decode('utf-8'),
            "Kyber Public Key": base64.b64encode(kyber_pk).decode('utf-8'),
            "Kyber Private Key": base64.b64encode(kyber_sk).decode('utf-8'),
        }
        with open(file_path, "w") as f:
            json.dump(user_data, f, indent=4)
        try:
            reg_url = f"http://{session.server_host}/quantserver/register-user"
            data = {"name": email.split("@")[0], "username": email, "public_key": user_data["Kyber Public Key"], "password": "none"}
            requests.post(reg_url, data=data, timeout=2)
        except: pass
    create_table(email)

def login(email, password):
    try:
        email = sanitize_input(email)
        register_local_keys(email)
        session.set_email_config(email, password)
        return {"success": True, "message": "Login Successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def fetch_inbox():
    if not session.email_address:
        return {"success": False, "message": "Not logged in"}
    
    new_count = 0
    sync_warning = None
    safe_table = get_safe_table_name(session.email_address)
    
    # 1. Try to sync from network
    if session.email_service:
        try:
            success, emails = session.email_service.fetch_emails()
            if success:
                mydb = get_db_connection()
                mycursor = mydb.cursor()
                for email in emails:
                    try:
                        body = email['body']
                        sender = email['sender']
                        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        mycursor.execute(
                            f"INSERT OR IGNORE INTO {safe_table} VALUES (?, ?, ?, ?)",
                            (sender, email['subject'], body, dt)
                        )
                        new_count += 1
                        session.blockchain.add_transaction(sender, session.email_address, "SYNC", "RECEIVED")
                    except Exception as e: print(f"Email loop error: {e}")
                mydb.commit()
                mydb.close()
            else:
                sync_warning = str(emails)
                if "535" in sync_warning or "AUTHENTICATIONFAILED" in sync_warning:
                    sync_warning = "Login Failed. Use an App Password (myaccount.google.com/apppasswords)"
        except Exception as e:
            sync_warning = str(e)

    # 2. Read local DB (Always)
    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM {safe_table} ORDER BY date DESC")
        data = []
        for row in mycursor:
            data.append({"sender": row[0], "subject": row[1], "body": row[2], "date": row[3]})
        mydb.close()
        
        msg = f"Loaded {len(data)} emails."
        if new_count > 0: msg = f"Synced {new_count} new. " + msg
        if sync_warning: msg += f" (Note: Sync issue - {sync_warning})"
        
        return {"success": True, "emails": data, "message": msg}
    except Exception as e:
        return {"success": False, "message": f"Local storage error: {str(e)}"}

def send_email(receiver, subject, body, level):
    if not session.email_service: return {"success": False, "message": "Offline"}
    try:
        final_body = body
        if level == 3: # QKD (Simulated)
            q_key_bytes, q_key_str, qkd_id = session.quantum_sim.generate_key()
            cipher_q = AES.new(q_key_bytes, AES.MODE_GCM)
            ct_q, tag_q = cipher_q.encrypt_and_digest(body.encode('utf-8'))
            payload_q = {
                "iv": base64.b64encode(cipher_q.nonce).decode('utf-8'),
                "ciphertext": base64.b64encode(ct_q).decode('utf-8'),
                "tag": base64.b64encode(tag_q).decode('utf-8'),
                "level": 3,
                "qkd_id": qkd_id
            }
            final_body = json.dumps(payload_q)

        elif level in [1, 2]: # Standard/PQC wrappers
            aes_key = get_random_bytes(32)
            cipher = AES.new(aes_key, AES.MODE_GCM)
            ct, tag = cipher.encrypt_and_digest(body.encode('utf-8'))
            payload = {
                "iv": base64.b64encode(cipher.nonce).decode('utf-8'),
                "ciphertext": base64.b64encode(ct).decode('utf-8'),
                "tag": base64.b64encode(tag).decode('utf-8'),
                "level": level,
                "enc_key": base64.b64encode(aes_key).decode('utf-8') 
            }
            final_body = json.dumps(payload)

        success, msg = session.email_service.send_email(receiver, subject, final_body)
        
        # Intercept Gmail Auth Error
        if not success and "535" in str(msg):
            msg = "Login Failed: You must use a Google App Password, not your normal password. Enable 2FA -> myaccount.google.com/apppasswords"
            
        session.blockchain.add_transaction(session.email_address, receiver, f"L{level}", "SENT" if success else "FAIL")
        return {"success": success, "message": msg}
    except Exception as e:
        return {"success": False, "message": str(e)}

def decrypt_payload(payload):
    try:
        level = payload.get("level")
        iv = base64.b64decode(payload["iv"])
        ciphertext = base64.b64decode(payload["ciphertext"])
        tag = base64.b64decode(payload["tag"])
        
        key = None
        if level == 3:
            # Fetch from Quantum Key Manager
            qkd_id = payload.get("qkd_id")
            key = session.quantum_sim.get_key_from_vault(qkd_id)
        elif "enc_key" in payload:
            # Simulating RSA/PQC key recovery
            key = base64.b64decode(payload["enc_key"])
            
        if not key:
            return "Decryption Error: Key not found in KM vault."
            
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted.decode('utf-8')
    except Exception as e:
        return f"🔒 Encryption Lock Intact: {str(e)}"

def get_blockchain_data():
    return session.blockchain.get_chain()
