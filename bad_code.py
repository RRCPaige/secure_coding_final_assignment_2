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



# CWE-798: Use of Hard-coded Credentials
SECRET_KEY = "supersecretkey123"
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef1234567890abcdef"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# CWE-312: Cleartext Storage of Sensitive Information
def store_sensitive_data(credit_card, ssn):
    """A02 - Storing PII/sensitive data in plaintext."""
    with open("user_data.txt", "w") as f:
        f.write(f"CC: {credit_card}\nSSN: {ssn}\n")



# CWE-89: SQL Injection (f-string variant)
def login(username, password):
    """A03 - SQL injection in login — allows authentication bypass."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"  # VULN
    cursor.execute(query)
    return cursor.fetchone()



# CWE-284: Improper Access Control
_user_database = {
    1: {"name": "Alice", "role": "admin", "salary": 95000},
    2: {"name": "Bob",   "role": "user",  "salary": 55000},
    3: {"name": "Carol", "role": "user",  "salary": 60000},
}

def get_user_data(requested_user_id, current_user_id):
    """A01 - IDOR: no check that current_user owns the requested record."""
    return _user_database.get(requested_user_id)  # VULN: missing ownership check

# CWE-862: Missing Authorization
def delete_user(user_id):
    """A01 - No admin role check before performing privileged action."""
    if user_id in _user_database:
        del _user_database[user_id]
        return f"User {user_id} deleted."
    return "User not found."



# CWE-307: Improper Restriction of Excessive Authentication Attempts
def authenticate(username, password, attempts={}):
    """A07 - No rate limiting or account lockout on failed logins."""
    # No lockout logic whatsoever
    stored_hash = hash_password_weak(password)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password_hash='{stored_hash}'"  # VULN: SQL + weak hash
    cursor.execute(query)
    return cursor.fetchone()

# CWE-330: Use of Insufficiently Random Values
def generate_session_token(username):
    """A07 - Predictable session token based on username + weak hash."""
    return hashlib.md5(f"{username}session".encode()).hexdigest()  # VULN

# CWE-613: Insufficient Session Expiration
SESSION_STORE = {}

def create_session(user_id):
    """A07 - Session never expires."""
    token = generate_session_token(str(user_id))
    SESSION_STORE[token] = {"user_id": user_id}  # VULN: no expiry, no invalidation
    return token

def get_session(token):
    return SESSION_STORE.get(token)


# CWE-502: Deserialization of Untrusted Data
def load_user_object(serialized_data):
    """A08 - Unsafe pickle deserialization allows arbitrary code execution."""
    return pickle.loads(serialized_data)  # VULN: never unpickle untrusted data

def save_user_object(user_obj):
    return pickle.dumps(user_obj)

# CWE-502: YAML deserialization (unsafe load)
def load_config(yaml_string):
    """A08 - yaml.load without Loader allows code execution."""
    return yaml.load(yaml_string)  # VULN: should use yaml.safe_load


def verbose_error_handler(e):
    """A05 - Full stack trace returned to the client."""
    import traceback
    return traceback.format_exc()  # VULN: leaks internals to attackers


# CWE-532: Insertion of Sensitive Information into Log File
def process_payment(card_number, cvv, amount):
    """A09 - Logs full card number and CVV — PCI violation."""
    logging.info(f"Processing payment: card={card_number} cvv={cvv} amount={amount}")  # VULN
    return {"status": "charged", "amount": amount}


# CWE-918: Server-Side Request Forgery
def fetch_url(url):
    """A10 - SSRF: fetches any URL including internal cloud metadata endpoints."""
    # Attacker can supply: http://169.254.169.254/latest/meta-data/
    response = urllib.request.urlopen(url)  # VULN: no allowlist, no IP restriction
    return response.read()


def transfer_funds(from_account, to_account, amount):
    """A04 - No check that amount > 0; negative transfer = stealing funds."""
    # Missing: if amount <= 0: raise ValueError(...)
    from_account["balance"] -= amount  # VULN: no negative-amount guard
    to_account["balance"] += amount
    return from_account, to_account



if __name__ == "__main__":
    print("=" * 60)
    print("OWASP Top 10 Vulnerable Demo — DO NOT USE IN PRODUCTION")
    print("=" * 60)


    # A03 — SQLi payload example (not executed against real DB here)
    print(f"\n[A03] SQLi payload would be: ' OR '1'='1")

    # A07 — Predictable token
    print(f"\n[A07] Predictable session token for 'admin': {generate_session_token('admin')}")


    print("\nRun a SAST scanner (e.g. Bandit, Semgrep) against this file to see findings.")