from flask import Flask, request, jsonify, session, render_template, send_file
from functools import wraps
from flask import jsonify, session
from datetime import datetime
import uuid
import hashlib
import io
import csv
import re


from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://sayjopvmessbkleeuevi.supabase.co"
SUPABASE_KEY = "sb_publishable_IR1o97XPiLFsnYLO2X_1cQ_57V2KKFF"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = "secret123"

#  HELPERS 
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

#  AUTHENTICATION
@app.route("/api/register", methods=["POST"])
def register():
    d = request.json

    user_id = str(uuid.uuid4())[:8].upper()

    existing = supabase.table("users") \
        .select("*") \
        .or_(f"email.eq.{d['email']},username.eq.{d['username']},contact.eq.{d['contact']}") \
        .execute()

   

    if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', d["email"]):
        return jsonify({"error": "Only valid Gmail accounts allowed"}), 400
    if existing.data:
        return jsonify({"error": "User already exists"}), 409

    supabase.table("users").insert({
        "user_id": user_id,
        "username": d["username"],
        "name": d["name"],
        "email": d["email"],
        "contact": d["contact"],
        "password_hash": hash_password(d["password"])
    }).execute()

    session["user_id"] = user_id
    session["username"] = d["username"]

    return jsonify({"message": "Registered"})

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    identifier = d["identifier"]

    res = supabase.table("users") \
        .select("*") \
        .or_(f"email.eq.{identifier},username.eq.{identifier},contact.eq.{identifier}") \
        .execute()

    if not res.data:
        return jsonify({"error": "User not found"}), 404

    user = res.data[0]

    if user["password_hash"] != hash_password(d["password"]):
        return jsonify({"error": "Wrong password"}), 401

    session["user_id"] = user["user_id"]
    session["username"] = user["username"]

    return jsonify({"message": "Login success"})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# EXPENSE 
@app.route("/api/expenses", methods=["GET"])
@login_required
def get_expenses():
    res = supabase.table("expenses") \
        .select("*") \
        .eq("user_id", session["user_id"]) \
        .order("date", desc=True) \
        .execute()

    return jsonify(res.data)

@app.route("/api/expenses", methods=["POST"])
@login_required
def add_expense():
    d = request.json

    exp = {
        "expense_id": str(uuid.uuid4())[:12],
        "user_id": session["user_id"],
        "amount": float(d["amount"]),
        "category": d.get("category", "Other"),
        "description": d.get("description", "Expense"),
        "date": datetime.now().isoformat(),
        "source": d.get("source", "text")
    }

    supabase.table("expenses").insert(exp).execute()

    return jsonify({"message": "Saved"})

@app.route("/api/expenses/<expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    supabase.table("expenses") \
        .delete() \
        .eq("expense_id", expense_id) \
        .execute()

    return jsonify({"message": "Deleted"})

# CSV EXPORT 
@app.route("/api/expenses/export", methods=["GET"])
@login_required
def export_expenses():
    res = supabase.table("expenses") \
        .select("*") \
        .eq("user_id", session["user_id"]) \
        .execute()

    rows = res.data

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Description", "Category", "Amount", "Source"])

    for r in rows:
        writer.writerow([
            r["date"],
            r["description"],
            r["category"],
            r["amount"],
            r["source"]
        ])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="expenses.csv"
    )

@app.route("/api/me", methods=["GET"])
@login_required
def get_profile():
    res = supabase.table("users") \
        .select("*") \
        .eq("user_id", session["user_id"]) \
        .execute()

    if not res.data:
        return jsonify({"error": "User not found"}), 404

    return jsonify(res.data[0])


#FRONTEND 
@app.route("/")
def index():
    return render_template("index.html")

#  RUN 
if __name__ == "__main__":
    app.run(debug=True)