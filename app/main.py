import os
import jwt
import bcrypt
import datetime
import functools
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

db = SQLAlchemy(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set!")

FERNET_KEY = os.environ.get("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode()) if FERNET_KEY else None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Secret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"message": "Token missing ❌"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired ❌"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token ❌"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return {"status": "SecureVault running"}

@app.route("/init-db")
def init_db():
    db.create_all()
    return {"database": "tables created ✅"}

@app.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.json
    existing = User.query.filter_by(username=data["username"]).first()
    if existing:
        return jsonify({"message": "Username already taken ❌"}), 409
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
    user = User(username=data["username"], password=hashed.decode())
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created ✅"}), 201

@app.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and bcrypt.checkpw(data["password"].encode(), user.password.encode()):
        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials ❌"}), 401

@app.route("/me")
@token_required
def me():
    user = User.query.get(request.user_id)
    return jsonify({"id": user.id, "username": user.username})

@app.route("/secrets", methods=["POST"])
@token_required
def store_secret():
    data = request.json
    value = fernet.encrypt(data["value"].encode()).decode() if fernet else data["value"]
    secret = Secret(user_id=request.user_id, name=data["name"], value=value)
    db.session.add(secret)
    db.session.commit()
    return jsonify({"message": "Secret stored ✅"}), 201

@app.route("/secrets", methods=["GET"])
@token_required
def get_secrets():
    secrets = Secret.query.filter_by(user_id=request.user_id).all()
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "value": fernet.decrypt(s.value.encode()).decode() if fernet else s.value
    } for s in secrets])

@app.route("/secrets/<int:secret_id>", methods=["DELETE"])
@token_required
def delete_secret(secret_id):
    secret = Secret.query.filter_by(id=secret_id, user_id=request.user_id).first()
    if not secret:
        return jsonify({"message": "Secret not found ❌"}), 404
    db.session.delete(secret)
    db.session.commit()
    return jsonify({"message": "Secret deleted ✅"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)