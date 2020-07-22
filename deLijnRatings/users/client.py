from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from passlib.hash import sha256_crypt
from sqlalchemy import exc
from sqlalchemy.sql import func

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres:postgres@users-db:5432/users"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

###################################### ENCRYPTION ######################################

def encrypt_password(password):
	return sha256_crypt.hash(password)

def check_encrypted_password(password, hashed):
	return sha256_crypt.verify(password, hashed)

###################################### USER MODEL ######################################

class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	password = db.Column(db.String(128), nullable=False)
	active = db.Column(db.Boolean(), default=True, nullable=False)
	created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

	def __init__(self, username, email, password):
		self.username = username
		self.email = email
		self.password = encrypt_password(password)

	def to_json(self):
		return {
			'id': self.id,
			'username': self.username,
			'email': self.email,
			'active': self.active
		}

###################################### RESOURCES ######################################
class getAllUsers(Resource):
	def get(self):
		response_object = {
			'status': 'success',
			'data': {
				'users': [user.to_json() for user in User.query.all()]
			}
		}
		return jsonify(response_object)

class verifyUser(Resource):
	def get(self, username):
		password = request.get_json()["password"]

		response_object = {
			'status': 'fail',
			'message': 'Username-Password combination not found.'
		}	
		
		hashed = User.query.filter_by(username=username).first()

		if hashed:
			if check_encrypted_password(password, hashed.password):
				response_object['status'] = 'success'
				response_object['message'] = 'User found, password correct.'
				return jsonify(response_object)

			else:
				return jsonify(response_object)

		else:
			response_object['message'] = 'Username not found.'
			return jsonify(response_object)

class registerUser(Resource):
	def post(self, username, email, password):
		response_object = {
			'status': 'fail',
			'message': 'Something went wrong. Please try again.'
		}

		try:
			user = User.query.filter_by(email=email).first()
			if user:
				response_object['message'] = 'Sorry, that email already exists.'
				return jsonify(response_object)
			else:
				user = User.query.filter_by(username=username).first()

				if user:
					response_object['message'] = 'Sorry, that username already exists.'
					return jsonify(response_object)
				else:
					db.session.add(User(username=username, email=email, password=password))
					db.session.commit()
					response_object['status'] = 'success'
					response_object['message'] = f'{email} was added!'
					return jsonify(response_object)

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)
			
		return jsonify(response_object)

api.add_resource(getAllUsers, '/all_users')
api.add_resource(verifyUser, '/verify_user/<username>')
api.add_resource(registerUser, '/register/<username>/<email>/<password>')