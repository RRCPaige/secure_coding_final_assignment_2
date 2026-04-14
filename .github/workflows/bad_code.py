""""
This is going to be bad code not in standard with OWASP 2025.
"""
import sqlite3

ACCOUNTS = {
    1001: {"id": 1, "name": "alice"},
    1002: {"id": 2, "name": "bob"},
    1003: {"id": 3, "name": "carl"}
}

def get_balance(account_number):
    # INSECURE: No authentication, no authorization, no identity check
    return ACCOUNTS.get(account_number, {"error": "Account not found"})
BANK_PIN = "1234"  # INSECURE: hardcoded secret

def system_info():
    # INSECURE: exposes sensitive internal details
    return {
        "debug_mode": True,
        "hardcoded_pin": BANK_PIN,
        "accounts_loaded": list(ACCOUNTS.keys()),
    }
DB = "bank.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, acct INT, amount INT)")
    conn.commit()
    conn.close()

def get_transactions(acct_number):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # INSECURE: direct string concatenation allows SQL injection
    query = f"SELECT id, acct, amount FROM transactions WHERE acct = {acct_number}"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Broken Access Control:", get_balance(1002))
    print("Security Misconfiguration:", system_info())
    print("SQL Injection:", get_transactions("1001"))