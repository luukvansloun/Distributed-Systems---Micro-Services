from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import requests
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
from operator import itemgetter

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres:postgres@delijn-db:5432/delijn"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

###################################### URLS ######################################

# De Lijn API Routing URLs
deLijnURLs = {
	"provinces": "https://api.delijn.be/DLKernOpenData/api/v1/entiteiten",
	"stopsForProvince": "https://api.delijn.be/DLKernOpenData/api/v1/entiteiten/{entiteitnummer}/haltes",
	"linesForProvince": "https://api.delijn.be/DLKernOpenData/api/v1/entiteiten/{entiteitnummer}/lijnen",
	"lineDirections": "https://api.delijn.be/DLKernOpenData/api/v1/lijnen/{entiteitnummer}/{lijnnummer}/lijnrichtingen",
	"stopsForLine": "https://api.delijn.be/DLKernOpenData/api/v1/lijnen/{entiteitnummer}/{lijnnummer}/lijnrichtingen/{richting}/haltes",
	"towns": "https://api.delijn.be/DLKernOpenData/api/v1/gemeenten",
	"stopsForTown": "https://api.delijn.be/DLKernOpenData/api/v1/gemeenten/{gemeenteNummer}/haltes"
}

headers = {
	"Ocp-Apim-Subscription-Key": "e855ca5e78074b8ca624b4a09c830985"
}

###################################### MODELS ######################################
class Stop(db.Model):
	__tablename__ = 'stops'

	stopID = db.Column(db.Integer, primary_key=True, nullable=False)
	description = db.Column(db.String(128), nullable=False)
	townDescription = db.Column(db.String(128), nullable=False)

	def __init__(self, stopID, description, townDescription):
		self.stopID = stopID
		self.description = description
		self.townDescription = townDescription

	def to_json(self):
		return {
			'id': self.stopID,
			'description': self.description,
			'townDescription': self.townDescription
		}

###################################### RESOURCES ######################################

# Fill DB Tables with Towns & Stops to prevent long loading times on site
def setupDatabaseTables():
	provinces = requests.get(url=deLijnURLs["provinces"], headers=headers).json()
	
	for p in provinces["entiteiten"]:
		url = deLijnURLs["stopsForProvince"].format(entiteitnummer=p["entiteitnummer"])
		stops = requests.get(url=url, headers=headers).json()

		for stop in stops["haltes"]:
			__tablename__ = "stops"
			try:
				try:
					db.session.add(Stop(stopID=stop["haltenummer"], description=stop["omschrijving"], townDescription=stop["omschrijvingGemeente"]))
				except NameError:
					continue
			except KeyError:
				continue
	
	db.session.commit()


# Get all Provinces
class getProvinces(Resource):
	def get(self):
		return requests.get(url=deLijnURLs["provinces"], headers=headers).json()

# Get all Lines in a specific Province
class getLinesForProvince(Resource):
	def get(self, provinceNumber):
		requestData = requests.get(url=deLijnURLs["linesForProvince"].format(entiteitnummer=provinceNumber),
									headers=headers).json()

		lines = []
		for line in requestData["lijnen"]:
			if line["publiek"]:
				lineData = {}
				lineData["privlinenumber"] = line["lijnnummer"]
				lineData["linenumber"] = line["lijnnummerPubliek"]
				lineData["description"] = line["omschrijving"]
				lines.append(lineData)

		lines = sorted(lines, key=itemgetter('linenumber'))

		return jsonify({'lines' : lines})

# Retrieve the possible directions for the requested line
class getLineDirections(Resource):
	def get(self, provinceNumber, lineNumber):
		requestData = requests.get(url=deLijnURLs["lineDirections"].format(entiteitnummer=provinceNumber, lijnnummer=lineNumber),
									headers=headers).json()

		directions = []
		for direction in requestData["lijnrichtingen"]:
			dirData = {}
			dirData["direction"] = direction["richting"]
			dirData["destination"] = direction["bestemming"]
			directions.append(dirData)

		directions = sorted(directions, key=itemgetter('direction'))

		return jsonify({'directions': directions})

# Retrieve all the stops and their info for the requested line
class getStopsForLine(Resource):
	def get(self, provinceNumber, lineNumber, direction):
		# Request the different data
		requestData = requests.get(url=deLijnURLs["stopsForLine"].format(entiteitnummer=provinceNumber, lijnnummer=lineNumber,
									richting=direction), headers=headers).json()
		# Setup stop collection
		stops = []
		for i in range(len(requestData["haltes"])):
			stopData = {}
			stopData["stopNumber"] = requestData["haltes"][i]["haltenummer"]
			stopData["description"] = requestData["haltes"][i]["omschrijving"]

			stops.append(stopData)

		returnData = {
			"stops": stops
		}

		return jsonify(returnData)

class getAllStops(Resource):
	def get(self):
		response_object = {
			'status': 'success',
			'stops': [stop.to_json() for stop in Stop.query.all()]
		}
		return jsonify(response_object)

class getAllTowns(Resource):
	def get(self):
		response_object = {
			'status': 'success',
			'towns': [stop.townDescription for stop in Stop.query.distinct(Stop.townDescription)]
		}
		return jsonify(response_object)

class getStopsForTown(Resource):
	def get(self, townDescription):
		# Setup stop collection
		response_object = {
			'status': 'success',
			'stops': [stop.to_json() for stop in Stop.query.filter_by(townDescription=townDescription)]
		}
		return jsonify(response_object)

# Add API resources
api.add_resource(getProvinces, '/provinces')
api.add_resource(getLinesForProvince, '/provinces/<provinceNumber>/lines')
api.add_resource(getLineDirections, '/<provinceNumber>/lines/<lineNumber>/directions')
api.add_resource(getStopsForLine, '/<provinceNumber>/lines/<lineNumber>/directions/<direction>')
api.add_resource(getStopsForTown, '/towns/<townDescription>')
api.add_resource(getAllStops, '/stops')
api.add_resource(getAllTowns, '/towns')