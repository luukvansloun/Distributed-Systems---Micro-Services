from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from sqlalchemy import exc
from sqlalchemy.sql import func

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres:postgres@ratings-db:5432/ratings"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

###################################### RATING MODELS ######################################
class Vehicle(db.Model):
	__tablename__ = 'vehicles'

	vehicleID = db.Column(db.Integer, primary_key=True, nullable=False)
	vehicleType = db.Column(db.String(128), nullable=False)
	created_by = db.Column(db.String(128), nullable=False)

	def __init__(self, vehicleID, vehicleType, created_by):
		self.vehicleID = vehicleID
		self.vehicleType = vehicleType
		self.created_by = created_by

	def to_json(self):
		return {
			'id': self.vehicleID,
			'type': self.vehicleType,
			'created_by': self.created_by
		}

class VehicleRating(db.Model):
	__tablename__ = 'vehicleratings'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	vehicleID = db.Column(db.Integer, nullable=False)
	vehicleType = db.Column(db.String(128), nullable=False)
	rating = db.Column(db.Integer, nullable=False)
	user = db.Column(db.String(128), nullable=False)
	created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

	def __init__(self, vehicleID, vehicleType, rating, user):
		self.vehicleID = vehicleID
		self.vehicleType = vehicleType
		self.rating = rating
		self.user = user

	def to_json(self):
		return {
			'id': self.vehicleID,
			'type': self.vehicleType,
			'rating': self.rating,
			'user': self.user
		}

class StopRating(db.Model):
	__tablename__ = 'stopratings'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	stopID = db.Column(db.Integer, nullable=False)
	rating = db.Column(db.Integer, nullable=False)
	user = db.Column(db.String(128), nullable=False)
	created_date = db.Column(db.DateTime, default=func.now(), nullable=False)

	def __init__(self, stopID, rating, user):
		self.stopID = stopID
		self.rating = rating
		self.user = user

	def to_json(self):
		return {
			'id': self.stopID,
			'rating': self.rating,
			'user': self.user
		}

###################################### RESOURCES ######################################
class addVehicle(Resource):
	def post(self, vehicleID, vehicleType, created_by):

		response_object = {
			'status': 'fail',
			'message': 'Something went wrong, please try again.'
		}

		try:
			v = Vehicle.query.filter_by(vehicleID=vehicleID).first()
			if v:
				response_object["message"] = "Vehicle already exists."
				return jsonify(response_object)
			else:
				db.session.add(Vehicle(vehicleID=vehicleID, vehicleType=vehicleType, created_by=created_by))
				db.session.commit()
				response_object["status"] = "success"
				response_object["message"] = "Vehicle was successfully added!"
				return jsonify(response_object)

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)
			
		return jsonify(response_object)

class removeVehicle(Resource):
	def post(self, vehicleID, created_by):

		response_object = {
			'status': 'fail',
			'message': 'Something went wrong, please try again.'
		}

		try:
			v = Vehicle.query.filter_by(vehicleID=vehicleID).first()
			if not v:
				response_object["message"] = "Vehicle does not exist."
				return jsonify(response_object)
			else:
				if v.created_by != created_by:
					response_object["message"] = "User does not have the rights to remove the given vehicle."
					return jsonify(response_object)

				else:
					db.session.delete(v)
					db.session.commit()
					response_object["status"] = "success"
					response_object["message"] = "Vehicle was successfully deleted!"
					return jsonify(response_object)

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)
			
		return jsonify(response_object)

class getAllVehicles(Resource):
	def get(self):
		response_object = {
			'status': 'success',
			'vehicles': [vehicle.to_json() for vehicle in Vehicle.query.all()]
		}	
		return jsonify(response_object)

class addVehicleRating(Resource):
	def post(self):
		vehicleID = request.get_json()["vehicleID"]
		vehicleType = Vehicle.query.filter_by(vehicleID=vehicleID).first().vehicleType
		rating = request.get_json()["rating"]
		user = request.get_json()["user"]

		response_object = {
			'status': 'fail',
			'message': 'Something went wrong, please try again.'
		}

		try:
			r = VehicleRating.query.filter_by(user=user, vehicleID=vehicleID).first()
			# If rating already in DB, update
			if r:
				r.rating = rating
				response_object["status"] = "success"
				response_object["message"] = "Rating for given {} found and updated!".format(vehicleType)
				return jsonify(response_object)
			else:
				db.session.add(VehicleRating(vehicleID=vehicleID, vehicleType=vehicleType, rating=rating, user=user))
				db.session.commit()
				response_object["status"] = "success"
				response_object["message"] = "Rating for given {} added!".format(vehicleType)
				return jsonify(response_object)
		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)
			
		return jsonify(response_object)

class addStopRating(Resource):
	def post(self):
		stopID = request.get_json()["stopID"]
		rating = request.get_json()["rating"]
		username = request.get_json()["username"]

		response_object = {
			'status': 'fail',
			'message': 'Something went wrong, please try again.'
		}

		try:
			r = StopRating.query.filter_by(user=username, stopID=stopID).first()
			# If rating already in DB, update
			if r:
				r.rating = rating
				response_object["status"] = "success"
				response_object["message"] = "Rating for given stop found and updated!"
				return jsonify(response_object)
			else:
				db.session.add(StopRating(stopID=stopID, rating=rating, user=username))
				db.session.commit()
				response_object["status"] = "success"
				response_object["message"] = "Rating for given stop added!"
				return jsonify(response_object)
		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)
			
		return jsonify(response_object)

class getUserRatings(Resource):
	def get(self, username):
		response_object = {
			'status': 'fail',
			'message': 'Something went wrong. Please try again.',
			'data': None
		}

		anyRatings = True
		ratingsList = {
			'stops': [],
			'vehicles': []
		}

		try:
			stopRatings = StopRating.query.filter_by(user=username).all()
			if stopRatings:
				for r in stopRatings:
					ratingsList["stops"].append({
							'id': r.stopID,
							'rating': r.rating,
							'user': r.user
						})
				response_object["status"] = "success"
			else:
				anyRatings = False			

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)
	
		try:
			vehicleRatings = VehicleRating.query.filter_by(user=username).all()
			if vehicleRatings:
				for t in vehicleRatings:
					ratingsList["vehicles"].append({
							'id': t.vehicleID,
							'type': t.vehicleType,
							'rating': t.rating,
							'user': t.user
						})
				response_object["status"] = "success"
				
				response_object["message"] = "Ratings found for the given user."
				response_object["data"] = ratingsList				
			else:
				if not anyRatings:
					response_object["status"] = "fail"
					response_object["message"] = "No ratings found for the given user."
					return jsonify(response_object)
				else:
					response_object["message"] = "Ratings found for the given user."
					response_object["data"] = ratingsList

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)

		return jsonify(response_object)

class getVehicleRatings(Resource):
	def get(self, vehicleID):
		response_object = {
			'status': 'fail',
			'message': 'Something went wrong. Please try again.',
			'data': None,
			'avg': None
		}

		try:
			try:
				int(vehicleID)
			except ValueError:
				response_object["message"] = "Vehicle ID must be an integer."
				return jsonify(response_object)

			vehicleRatings = VehicleRating.query.filter_by(vehicleID=vehicleID).all()
			if vehicleRatings:
				totalratings = 0
				ratingsList = []
				for r in vehicleRatings:
					ratingsList.append({
							'id': r.vehicleID,
							'type': r.vehicleType,
							'rating': r.rating,
							'user': r.user
						})
					totalratings += r.rating
				response_object["status"] = "success"
				response_object["message"] = "Ratings found for the given vehicle."
				response_object["data"] = ratingsList
				response_object["avg"] =  totalratings / len(vehicleRatings)

				return jsonify(response_object)
			else:
				response_object["message"] = "No ratings found for the given vehicle."
				return jsonify(response_object)

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)

		return jsonify(response_object)

class getStopRatings(Resource):
	def get(self, stopID):
		response_object = {
			'status': 'fail',
			'message': 'Something went wrong. Please try again.',
			'data': None,
			'avg': None
		}

		try:
			try:
				int(stopID)
			except ValueError:
				response_object["message"] = "Stop ID must be an integer."
				return jsonify(response_object)

			stopRatings = StopRating.query.filter_by(stopID=stopID).all()
			if stopRatings:
				totalratings = 0
				ratingsList = []
				for r in stopRatings:
					ratingsList.append({
							'id': r.stopID,
							'rating': r.rating,
							'user': r.user
						})
					totalratings += r.rating
				response_object["status"] = "success"
				response_object["message"] = "Ratings found for the given stop."
				response_object["data"] = ratingsList
				response_object["avg"] =  totalratings / len(stopRatings)
				return jsonify(response_object)
			else:
				response_object["message"] = "No ratings found for the given stop."
				return jsonify(response_object)

		except exc.IntegrityError as e:
			db.session.rollback()
			return jsonify(response_object)

		return jsonify(response_object)

api.add_resource(addVehicle, '/add_vehicle/<vehicleID>/<vehicleType>/<created_by>')
api.add_resource(removeVehicle, '/remove_vehicle/<vehicleID>/<created_by>')
api.add_resource(getAllVehicles, '/all_vehicles')
api.add_resource(addVehicleRating, '/rate_vehicle')
api.add_resource(addStopRating, '/rate_stop')
api.add_resource(getUserRatings, '/user_ratings/<username>')
api.add_resource(getVehicleRatings, '/vehicle_ratings/<vehicleID>')
api.add_resource(getStopRatings, '/stop_ratings/<stopID>')
