import os
import hashlib
from bson.json_util import dumps
import datetime
from flask_cors import cross_origin
from db import *
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity



load_dotenv()

app = Flask(__name__)


jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)


@app.route('/', methods=["GET"])
def index():
	return "<p>Simple REST API</p>"


@app.route('/register/', methods=["POST"])
@cross_origin()
def register():

	new_user = request.get_json()
	new_user["password"] = hashlib.sha256(new_user['password'].encode("utf-8")).hexdigest()

	database_collection = db.users
	doc = database_collection.find_one({"email": new_user["email"]})
	if not doc:
		database_collection.insert_one(new_user)
		return jsonify({'msg': 'User created successfully'}), 201
	else:
		return jsonify({'msg': 'Username already exists'}), 409


@app.route('/login/', methods=["POST"])
@cross_origin()
def login():

	login_info = request.get_json()
        database_collection = db.users
	database_users = database_collection.find_one({'email': login_info['email']})
	if database_users:
		encrpted_password = hashlib.sha256(login_info['password'].encode("utf-8")).hexdigest()
		if encrpted_password == database_users['password']:
			access_token = create_access_token(identity=str(database_users['_id']))
			return jsonify(access_token=access_token), 200
	return jsonify({'msg': 'The username or password is incorrect'}), 401

@app.route('/template/', methods=["POST"])
@jwt_required()
def create_template():
	
	get_jwt_identity()

	template = request.get_json()

	template_data = {
		"template_name": template["template_name"],
		"subject": template["subject"],
		"body": template["body"]	
	}

	database_collection = db.users
	temp = database_collection.find_one({"template_name": template["template_name"]})
	if not temp:
		database_collection.insert_one(template)
		return jsonify({'msg': 'Template created successfully'}), 201
	else:
		return jsonify({'msg': 'Template already in collection'}), 409

	
@app.route('/template/', methods=["GET"])
@jwt_required()
def retrieve_all_templates():

	get_jwt_identity()

	holder = list()
	database_collection = db.users

	for i in database_collection.find():
		holder.append(i)
		i['_id'] = str(i['_id'])

	json_data = dumps(str(holder))
	return jsonify({'msg': 'Templates fetch successful', 'data':json_data}), 200


@app.route('/template/<id>', methods=["GET"])
@jwt_required()
def retrieve_one_template(id):

	get_jwt_identity()

	database_collection = db.users
	data = dumps(database_collection.find_one({"_id":ObjectId(id)}))
	if data:
		return jsonify({'msg': 'Template fetch successful', 'data':data}), 200
	else:
		return jsonify({'msg': 'Template does not exist in current collection'}), 500
		

@app.route('/template/<id>', methods=["PUT"])
@jwt_required()
def update_data(id):

	get_jwt_identity()

	req = request.get_json()

	database_collection = db.users
	template = database_collection.find_one({"_id":ObjectId(id)})
	if template:
		database_collection.update_one({"_id": template['_id']}, {'$set': {'template_name': req.get('template_name'), 'subject': req.get('subject'), 'body': req.get('body')}})
		return jsonify({'msg': 'template successfully updated.'}), 200
	else:
		return jsonify({'msg': 'nothing update applicable'}), 200


@app.route('/template/<id>', methods=["DELETE"])
@jwt_required()
def delete(id):

	get_jwt_identity()

	database_collection = db.users
	template = database_collection.find_one({"_id":ObjectId(id)})
	if template:
		database_collection.delete_one(template)
		return jsonify({'msg': 'template successfully removed'}), 200
	else:
		return jsonify({'msg': 'template missing from collection'}), 404
	

if __name__ == '__main__':
	app.run(threaded=True, port=5000)
