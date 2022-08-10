from db import *
import hashlib
from flask import Flask, request, jsonify
from flask_pymongo import pymongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
app = Flask(__name__)
jwt = JWTManager(app)

@app.route("/register", methods=["POST"])
def register():
    new_user = request.get_json()
    user_pwd = hashlib.sha256(new_user['password'].encode("utf-8")).hexdigest()
    new_user["password"] =  user_pwd

    current_collection = db.collection
    doc = current_collection.find_one({"email": new_user["email"]})
    if not doc:
        current_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
	    return jsonify({'msg': 'Username already exists'}), 409

@app.route("/login", methods=["POST"])
def login():
    user = request.get_json()
    user["password"] = hashlib.sha256(user["password"].encode("utf-8")).hexdigest()
    doc = user_collection.find_one({"username": user["username"]})
    if not doc:
        return jsonify({'msg': 'User does not exist'}), 404
    if doc["password"] == user["password"]:
        access_token = create_access_token(identity=user["username"])
        return jsonify({'token': access_token}), 200

if __name__ == '__main__':
	app.run(threaded=True, port=5000)