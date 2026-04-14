"""
OWASP Top 10 Vulnerable Python Application
===========================================
WARNING: This file is intentionally vulnerable for security scanning
and educational demonstration purposes ONLY.
DO NOT deploy or use this code in any production or real environment.

OWASP Top 10 (2021) vulnerabilities demonstrated:
A01 - Broken Access Control
A02 - Cryptographic Failures
A03 - Injection
A04 - Insecure Design
A05 - Security Misconfiguration
A06 - Vulnerable and Outdated Components
A07 - Identification and Authentication Failures
A08 - Software and Data Integrity Failures
A09 - Security Logging and Monitoring Failures
A10 - Server-Side Request Forgery (SSRF)
"""

import sqlite3
import subprocess
import hashlib
import os
import pickle
import logging
import urllib.request
import xml.etree.ElementTree as ET
import yaml
import re



SECRET_KEY = "supersecretkey123"
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef1234567890abcdef"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


def store_sensitive_data(credit_card, ssn):
    with open("user_data.txt", "w") as f:
        f.write(f"CC: {credit_card}\nSSN: {ssn}\n")




def login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"  
    cursor.execute(query)
    return cursor.fetchone()




_user_database = {
    1: {"name": "Alice", "role": "admin", "salary": 95000},
    2: {"name": "Bob",   "role": "user",  "salary": 55000},
    3: {"name": "Carol", "role": "user",  "salary": 60000},
}

def get_user_data(requested_user_id, current_user_id):
    return _user_database.get(requested_user_id)  


def delete_user(user_id):
    if user_id in _user_database:
        del _user_database[user_id]
        return f"User {user_id} deleted."
    return "User not found."


def authenticate(username, password, attempts={}):
    """A07 - No rate limiting or account lockout on failed logins."""
    # No lockout logic whatsoever
    stored_hash = hash_password_weak(password)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password_hash='{stored_hash}'" 
    cursor.execute(query)
    return cursor.fetchone()


def generate_session_token(username):
    return hashlib.md5(f"{username}session".encode()).hexdigest()  


SESSION_STORE = {}

def create_session(user_id):
    token = generate_session_token(str(user_id))
    SESSION_STORE[token] = {"user_id": user_id}  
    return token

def get_session(token):
    return SESSION_STORE.get(token)



def load_user_object(serialized_data):
    
    return pickle.loads(serialized_data)  

def save_user_object(user_obj):
    return pickle.dumps(user_obj)

def load_config(yaml_string):
    return yaml.load(yaml_string)  


def verbose_error_handler(e):
    """A05 - Full stack trace returned to the client."""
    import traceback
    return traceback.format_exc()  



def process_payment(card_number, cvv, amount):
    """A09 - Logs full card number and CVV — PCI violation."""
    logging.info(f"Processing payment: card={card_number} cvv={cvv} amount={amount}")  
    return {"status": "charged", "amount": amount}


def fetch_url(url):
    response = urllib.request.urlopen(url)  
    return response.read()


def transfer_funds(from_account, to_account, amount):
    from_account["balance"] -= amount  
    to_account["balance"] += amount
    return from_account, to_account



if __name__ == "__main__":
    print("=" * 60)
    print("OWASP Top 10 Vulnerable Demo — DO NOT USE IN PRODUCTION")
    print("=" * 60)
    
    print(f"\n[A03] SQLi payload would be: ' OR '1'='1")

    print(f"\n[A07] Predictable session token for 'admin': {generate_session_token('admin')}")

    print("\nRun a SAST scanner (e.g. Bandit, Semgrep) against this file to see findings.")