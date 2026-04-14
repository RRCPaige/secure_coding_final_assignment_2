from flask import Flask, request, redirect, make_response, session, render_template_string
import sqlite3
import os
import subprocess
import pickle
import logging
import requests
import random
import hashlib
import tempfile
import yaml

app = Flask(__name__)

app.secret_key = "hardcoded_insecure_secret_key"
app.debug = True

PAYMENT_API_KEY = "sk_test_hardcoded_api_key"  
ADMIN_PASSWORD = "P@ssw0rd123"  

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("vulnerable_app")

def get_db_connection():
    conn = sqlite3.connect("app_data.db")
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'plaintextpassword')")
    conn.commit()
    conn.close()

init_db()

@app.route("/search_user")
def search_user():
    username = request.args.get("username", "")
    conn = get_db_connection()
    c = conn.cursor()
    query = f"SELECT id, username FROM users WHERE username = '{username}'"
    logger.debug("Executing query: %s", query)
    try:
        c.execute(query)
        rows = c.fetchall()
    finally:
        conn.close()
    return {"results": rows}

@app.route("/greet")
def greet():
    name = request.args.get("name", "<unknown>")
    template = "<h1>Hello, %s</h1>" % name
    return render_template_string(template)

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    cmd = "ping -c 1 " + host
    logger.debug("Running command: %s", cmd)
    status = os.system(cmd)
    return {"status": status}

@app.route("/load_object", methods=["POST"])
def load_object():
    data = request.data
    try:
        obj = pickle.loads(data)
        return {"loaded": str(obj)}
    except Exception as e:
        logger.exception("Failed to unpickle data")
        return {"error": "invalid data"}, 400

@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return {"error": "no url provided"}, 400
    try:
        resp = requests.get(url, timeout=5, verify=False)
        return resp.text
    except Exception as e:
        logger.exception("fetch failed")
        return {"error": "fetch failed"}, 500

@app.route("/read_file")
def read_file():
    path = request.args.get("path", "")
    try:
        with open(path, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        logger.exception("file read error")
        return {"error": "cannot read file"}, 400

@app.route("/update_profile", methods=["POST"])
def update_profile():
    username = request.form.get("username")
    bio = request.form.get("bio")
    with open("profiles.txt", "a") as f:
        f.write(f"{username}:{bio}\n")
    return {"status": "updated"}

@app.route("/go")
def go():
    target = request.args.get("next", "/")
    return redirect(target)

def hash_password_md5(password):
    return hashlib.md5(password.encode()).hexdigest()

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    hashed = hash_password_md5(password)
    with open("users.txt", "a") as f:
        f.write(f"{username}:{hashed}\n")
    return {"status": "registered"}

@app.route("/admin")
def admin():
    pwd = request.args.get("pwd")
    if pwd == ADMIN_PASSWORD:
        return {"admin": "welcome"}
    else:
        return {"admin": "denied"}, 403

def generate_token():
    return str(random.random())

@app.route("/get_token")
def get_token():
    token = generate_token()
    logger.debug("Generated token: %s", token)
    return {"token": token}

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return {"error": "no file"}, 400
    filename = f.filename
    save_path = os.path.join("uploads", filename)
    f.save(save_path)
    return {"saved": save_path}

@app.route("/extract")
def extract():
    archive = request.args.get("archive")
    extracted_path = os.path.join("extracted", archive)
    return {"extracted": extracted_path}

@app.route("/parse_yaml", methods=["POST"])
def parse_yaml():
    data = request.data.decode("utf-8")
    try:
        obj = yaml.load(data, Loader=yaml.FullLoader)
        return {"parsed": str(obj)}
    except Exception:
        logger.exception("yaml parse failed")
        return {"error": "invalid yaml"}, 400

@app.route("/tempfile_demo")
def tempfile_demo():
    tmpname = tempfile.mktemp() 
    with open(tmpname, "w") as f:
        f.write("temporary data")
    return {"tmp": tmpname}

@app.route("/calc")
def calc():
    expr = request.args.get("expr", "1+1")
    try:
        result = eval(expr)
        return {"result": str(result)}
    except Exception:
        logger.exception("eval failed")
        return {"error": "bad expression"}, 400

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    session["user"] = username
    resp = make_response({"status": "logged_in"})
    return resp

@app.route("/after_login")
def after_login():
    next_url = request.args.get("next", "/")
    return redirect(next_url)

@app.route("/run")
def run():
    cmd = request.args.get("cmd", "echo hello")
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
        return {"output": output.decode("utf-8")}
    except Exception:
        logger.exception("subprocess failed")
        return {"error": "command failed"}, 400

@app.errorhandler(500)
def internal_error(e):
    logger.exception("Internal server error")
    return {"error": "internal server error", "details": str(e)}, 500

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
 
 