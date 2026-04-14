"""
bad code
"""

import sqlite3

# -----------------------------------
# 1) A01 BROKEN ACCESS CONTROL
# -----------------------------------
# Any user can access ANY account by guessing the account number.

ACCOUNTS = {
    1001: {"owner": "Alice", "balance": 5000},
    1002: {"owner": "Bob", "balance": 1200},
}

def get_account_balance(acct_number):
    # INSECURE: no authentication, no authorization
    return ACCOUNTS.get(acct_number, {"error": "Account not found"})


# -----------------------------------
# 2) A02 SECURITY MISCONFIGURATION
# -----------------------------------
# Hardcoded password + debug info leak.

BANK_ADMIN_PASSWORD = "SuperSecret123"  # INSECURE: Bandit will flag this (B105)

def debug_settings():
    # INSECURE: exposes sensitive internal details
    return {
        "debug": True,
        "admin_password": BANK_ADMIN_PASSWORD,
        "accounts_loaded": list(ACCOUNTS.keys()),
    }


# -----------------------------------
# 3) A05 INJECTION (SQL Injection)
# -----------------------------------
# User input is placed directly into SQL.

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

    # INSECURE: SQL injection vulnerability (Bandit B608)
    query = f"SELECT id, acct, amount FROM transactions WHERE acct = {acct_number}"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return rows


# -----------------------------------
# Extra: exec() to guarantee Bandit detection
# -----------------------------------
def run_custom_rule(user_code):
    # INSECURE: Bandit will flag exec() (B102)
    exec(user_code)


# -----------------------------------
# Demo usage
# -----------------------------------
if __name__ == "__main__":
    init_db()
    print("Broken Access Control:", get_account_balance(1002))
    print("Security Misconfiguration:", debug_settings())
    print("SQL Injection:", get_transactions("1001"))
    run_custom_rule("print('Executing unsafe user code')")
