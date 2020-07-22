from flask import Flask, render_template, jsonify, request, url_for, redirect, flash
from flask_wtf import FlaskForm
from flask_cors import CORS
from wtforms import StringField, SelectField, PasswordField, IntegerField, HiddenField
from wtforms.validators import Length, InputRequired, EqualTo, Email
import requests

app = Flask(__name__, template_folder="./templates/")
CORS(app)
app.config.update(dict(
	SECRET_KEY = "\xbf\xcf\xde\xee\xe8\xc1\x8c\\\xfd\xe6\\!t^(\x1c/\xc6l\xe1,\xc9#\xd7",
	WTF_CSRF_SECRET_KEY = "Uei\xc2&\x8a\x18.H\x87\xc5\x1d\xd1\xc8\xc3\xcf\xe5\xfft_\x8c:\x03r"
))

########################################### FORMS ###########################################
class RegisterForm(FlaskForm):
	username = StringField('Username', [InputRequired(message="Username is required.")])
	email = StringField('Email', [InputRequired(message="Email address is required."),
								  Email(message="The supplied email address is not of a valid format.")])
	password = PasswordField('Password', [InputRequired("Password is required."),
										  EqualTo('passwordconfirm', message="Passwords do not match."),
										  Length(min=6, max=50, message="Password needs to be between 6 and 50 characters long.")])
	passwordconfirm = PasswordField('Confirm Password')

class VehicleAdditionForm(FlaskForm):
	vehicleID = IntegerField("Vehicle ID", [InputRequired(message="Stop ID is required.")])
	vehicleType = SelectField("Vehicle Type", choices=[("Bus", "Bus"), ("Tram", "Tram")])
	created_by = StringField('Username', [InputRequired(message="Username is required.")])
	password = PasswordField('Password', [InputRequired("Password is required.")])

class VehicleDeletionForm(FlaskForm):
	vehicle = SelectField("Vehicle", choices=[])
	created_by = StringField('Username', [InputRequired(message="Username is required.")])
	password = PasswordField('Password', [InputRequired("Password is required.")])

	def fillForm(self, vehicles):
		for v in vehicles:
			self.vehicle.choices.append((v[0], v[1]))

class VehicleRatingForm(FlaskForm):
	vehicle = SelectField("Vehicle", choices=[])
	rating = SelectField("Rating", choices=[("0", "0/5"), ("1", "1/5"), ("2", "2/5"), ("3", "3/5"), ("4", "4/5"), ("5", "5/5")])
	username = StringField('Username', [InputRequired(message="Username is required.")])
	password = PasswordField('Password', [InputRequired("Password is required.")])

	def fillForm(self, vehicles):
		for v in vehicles:
			self.vehicle.choices.append((v[0], v[1]))

class StopLineRatingForm(FlaskForm):
	provinces = requests.get(url="http://delijnapi:5000/provinces").json()

	provinceChoices = []
	for p in provinces['entiteiten']:
		provinceChoices.append((p['entiteitnummer'], p['omschrijving']))

	provinceField = SelectField('Province', choices=provinceChoices, id="province")
	lineField = SelectField('Line', coerce=str, choices=[], id="line")
	directionField = SelectField('Direction', coerce=str, choices=[], id="direction")
	stop = SelectField("Stop", coerce=str, choices=[], id="stopfield")
	rating = SelectField("Rating", choices=[("0", "0/5"), ("1", "1/5"), ("2", "2/5"), ("3", "3/5"), ("4", "4/5"), ("5", "5/5")])
	username = StringField('Username', [InputRequired(message="Username is required.")])
	password = PasswordField('Password', [InputRequired("Password is required.")])

	def fillLines(self, lines):
		for l in lines:
			self.lineField.choices.append((l[0], l[1]))

	def fillDirections(self, directions):
		for d in directions:
			self.directionField.choices.append((d[0], d[1]))

	def fillStops(self, stops):
		for s in stops:
			self.stop.choices.append((s[0], s[1]))

class StopAllRatingForm(FlaskForm):
	stop = SelectField("Stop", coerce=str, choices=[], id="stopfield")
	rating = SelectField("Rating", choices=[("0", "0/5"), ("1", "1/5"), ("2", "2/5"), ("3", "3/5"), ("4", "4/5"), ("5", "5/5")])
	username = StringField('Username', [InputRequired(message="Username is required.")])
	password = PasswordField('Password', [InputRequired("Password is required.")])

	def fillStops(self, stops):
		for s in stops:
			self.stop.choices.append((s[0], s[1]))

class StopTownRatingForm(FlaskForm):
	towns = requests.get(url="http://delijnapi:5000/towns").json()

	townChoices = []
	for t in towns['towns']:
		townChoices.append((t, t))

	town = SelectField("Town", coerce=str, choices=townChoices, id="townfield")
	stop = SelectField("Stop", coerce=str, choices=[], id="stopfield")
	rating = SelectField("Rating", choices=[("0", "0/5"), ("1", "1/5"), ("2", "2/5"), ("3", "3/5"), ("4", "4/5"), ("5", "5/5")])
	username = StringField('Username', [InputRequired(message="Username is required.")])
	password = PasswordField('Password', [InputRequired("Password is required.")])

	def fillStops(self, stops):
		for s in stops:
			self.stop.choices.append((s[0], s[1]))

class ProvinceLineForm(FlaskForm):
	provinces = requests.get(url="http://delijnapi:5000/provinces").json()

	provinceChoices = []
	for p in provinces['entiteiten']:
		provinceChoices.append((p['entiteitnummer'], p['omschrijving']))

	provinceField = SelectField('Province', choices=provinceChoices, id="province")
	lineField = SelectField('Line', coerce=str, choices=[], id="line")
	directionField = SelectField('Direction', coerce=str, choices=[], id="direction")

class searchForm(FlaskForm):
	searchterm = StringField("Search Term", [InputRequired(message="Search Term is required.")])
	searchtype = SelectField('Type', coerce=str, choices=[("user", "Username"), ("stop", "Stop"), ("vehicle", "Vehicle")])

########################################### ROUTES ###########################################
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def registerUser():
	register_form = RegisterForm(request.form) 

	if register_form.validate_on_submit():
		username = request.form["username"]
		email =  request.form["email"]
		password = request.form["password"]
		r = requests.post(url="http://users:5000/register/{}/{}/{}".format(username, email, password)).json()

		if r["status"] == "success":
			flash(message="You are now registered.", category="success")
			return redirect(url_for('index'))
		else:
			flash(message=r["message"], category="error")
			return render_template('register.html', register_form=register_form)
		
	else:
		return render_template('register.html', register_form=register_form)

@app.route('/ratings', methods=['GET', 'POST'])
def ratings():
	search_form = searchForm(request.form)

	if search_form.validate_on_submit():
		searchValue = request.form["searchterm"]
		searchType = request.form["searchtype"]

		if searchType == "user":
			userRatings = requests.get(url="http://ratings:5000/user_ratings/{}".format(searchValue)).json()

			if userRatings["status"] == "success" and userRatings["data"] is not None:
				stopList = []
				for stop in userRatings["data"]["stops"]:
					stopList.append(stop)

				vehicleList = []
				for vehicle in userRatings["data"]["vehicles"]:
					vehicleList.append(vehicle)

				return render_template('searchresults.html', searchValue=searchValue, searchType=searchType, stopList=stopList, vehicleList=vehicleList)
			else:
				flash(message=userRatings["message"], category="error")
				return render_template('ratings.html', search_form=search_form)
		elif searchType == "vehicle":
			vehicleRatings = requests.get(url="http://ratings:5000/vehicle_ratings/{}".format(searchValue)).json()

			if vehicleRatings["status"] == "success" and vehicleRatings["data"] is not None:
				vehicleList = []
				for vehicle in vehicleRatings["data"]:
					vehicleList.append(vehicle)

				average = str("{0:.1f}".format(vehicleRatings["avg"]))

				return render_template('searchresults.html', average=average, searchValue=searchValue, searchType=searchType, stopList=[], vehicleList=vehicleList)
			else:
				flash(message=vehicleRatings["message"], category="error")
				return render_template('ratings.html', search_form=search_form)

		elif searchType == "stop":
			stopRatings = requests.get(url="http://ratings:5000/stop_ratings/{}".format(searchValue)).json()

			if stopRatings["status"] == "success" and stopRatings["data"] is not None:
				stopList = []
				for stop in stopRatings["data"]:
					stopList.append(stop)

				average = str("{0:.1f}".format(stopRatings["avg"]))

				return render_template('searchresults.html', average=average, searchValue=searchValue, searchType=searchType, stopList=stopList, vehicleList=[])
			else:
				flash(message=stopRatings["message"], category="error")
				return render_template('ratings.html', search_form=search_form)

	else:
		return render_template('ratings.html', search_form=search_form)

@app.route('/addVehicle', methods=['GET', 'POST'])
def addVehicle():
	vehicle_add_form = VehicleAdditionForm(request.form)

	if vehicle_add_form.validate_on_submit():
		vehicleID = request.form["vehicleID"]
		vehicleType = request.form["vehicleType"]
		created_by = request.form["created_by"]
		password = request.form["password"]

		r = requests.get(url="http://users:5000/verify_user/{}".format(created_by), json={"password": password}).json()

		if r["status"] == "success":
			r2 = requests.post(url="http://ratings:5000/add_vehicle/{}/{}/{}".format(vehicleID, vehicleType, created_by)).json()

			if r2["status"] == "success":
				flash(message=r2["message"], category="success")
				return render_template('addVehicle.html', vehicle_add_form=VehicleAdditionForm())
			else:
				flash(message=r2["message"], category="error")
				return render_template('addVehicle.html', vehicle_add_form=vehicle_add_form)				

		else:
			flash(message=r["message"], category="error")
			return render_template('addVehicle.html', vehicle_add_form=vehicle_add_form)

	else:
		return render_template('addVehicle.html', vehicle_add_form=vehicle_add_form)

@app.route('/removeVehicle', methods=['GET', 'POST'])
def removeVehicle():
	vehicle_delete_form = VehicleDeletionForm(request.form)
	requestedVehicles = requests.get(url="http://ratings:5000/all_vehicles").json()["vehicles"]
	choices = []
	for v in requestedVehicles:
		choices.append((str(v["id"]), "{} {}".format(v["type"], v["id"])))
	vehicle_delete_form.fillForm(choices)

	if vehicle_delete_form.validate_on_submit():
		vehicleID = request.form["vehicle"]
		created_by = request.form["created_by"]
		password = request.form["password"]

		# Verify user
		r = requests.get(url="http://users:5000/verify_user/{}".format(created_by), json={"password": password}).json()

		if r["status"] == "success":
			r2 = requests.get(url="http://ratings:5000/vehicle_ratings/{}".format(vehicleID)).json()
			if r2["status"] == "success":
				if len(r2["data"]) == 1:
					r3 = requests.post(url="http://ratings:5000/remove_vehicle/{}/{}".format(vehicleID, created_by)).json()

					if r3["status"] == "success":
						vehicle_delete_form2 = VehicleDeletionForm()
						requestedVehicles2 = requests.get(url="http://ratings:5000/all_vehicles").json()["vehicles"]
						choices = []
						for v in requestedVehicles2:
							choices.append((str(v["id"]), "{} {}".format(v["type"], v["id"])))
						vehicle_delete_form2.fillForm(choices)
						flash(message=r3["message"], category="success")
						return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form2)
					else:
						flash(message=r3["message"], category="error")
						return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form)				

				else:
					flash(message="Vehicle cannot be deleted. More than 1 ratings submitted for the given vehicle.", category="error")
					return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form)

			else:
				r3 = requests.post(url="http://ratings:5000/remove_vehicle/{}/{}".format(vehicleID, created_by)).json()

				if r3["status"] == "success":
					vehicle_delete_form2 = VehicleDeletionForm()
					requestedVehicles2 = requests.get(url="http://ratings:5000/all_vehicles").json()["vehicles"]
					choices = []
					for v in requestedVehicles2:
						choices.append((str(v["id"]), "{} {}".format(v["type"], v["id"])))
					vehicle_delete_form2.fillForm(choices)
					flash(message=r3["message"], category="success")
					return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form2)
				else:
					flash(message=r3["message"], category="error")
					return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form)

		else:
			flash(message=r["message"], category="error")
			return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form)

	else:
		return render_template('removeVehicle.html', vehicle_delete_form=vehicle_delete_form)

@app.route('/rateVehicle', methods=['GET', 'POST'])
def rateVehicle():
	vehicle_rating_form = VehicleRatingForm(request.form)
	requestedVehicles = requests.get(url="http://ratings:5000/all_vehicles").json()["vehicles"]
	choices = []
	for v in requestedVehicles:
		choices.append((str(v["id"]), "{} {}".format(v["type"], v["id"])))
	vehicle_rating_form.fillForm(choices)

	if vehicle_rating_form.validate_on_submit():
		vehicleID = request.form["vehicle"]
		rating = request.form["rating"]
		username = request.form["username"]
		password = request.form["password"]

		r = requests.get(url="http://users:5000/verify_user/{}".format(username), json={"password": password}).json()

		if r["status"] == "success":
			ratingVars = {
				"vehicleID": vehicleID,
				"rating": rating,
				"user": username
			}

			r2 = requests.post(url="http://ratings:5000/rate_vehicle", json=ratingVars).json()

			if r2["status"] == "success":
				flash(message=r2["message"], category="success")
				return render_template('rateVehicle.html', vehicle_rating_form=vehicle_rating_form)
			else:
				flash(message=r2["message"], category="error")
				return render_template('rateVehicle.html', vehicle_rating_form=vehicle_rating_form)				

		else:
			flash(message=r["message"], category="error")
			return render_template('rateVehicle.html', vehicle_rating_form=vehicle_rating_form)

	else:
		return render_template('rateVehicle.html', vehicle_rating_form=vehicle_rating_form)

@app.route('/rateLineStop', methods=['GET', 'POST'])
def rateStopLine():
	stop_rating_form = StopLineRatingForm(request.form)

	if request.method == "POST":
		province = stop_rating_form.provinceField.data
		line = stop_rating_form.lineField.data
		direction = stop_rating_form.directionField.data

		requestedLines = requests.get(url="http://delijnapi:5000/provinces/{}/lines".format(province)).json()["lines"]
		linechoices = []
		for l in requestedLines:
			linechoices.append((l["privlinenumber"], "{}: {}".format(l["linenumber"], l["description"])))
		stop_rating_form.fillLines(linechoices)

		requestedDirections = requests.get(url="http://delijnapi:5000/{}/lines/{}/directions".format(province, line, direction)).json()["directions"]
		directionchoices = []
		for d in requestedDirections:
			directionchoices.append((d["direction"], "{}: {}".format(d["direction"], d["destination"])))
		stop_rating_form.fillDirections(directionchoices)

		requestedStops = requests.get(url="http://delijnapi:5000/{}/lines/{}/directions/{}".format(province, line, direction)).json()["stops"]
		stopchoices = []
		for s in requestedStops:
			stopchoices.append((s["stopNumber"], "{}: {}".format(s["stopNumber"], s["description"])))
		stop_rating_form.fillStops(stopchoices)

	if stop_rating_form.validate_on_submit():
		stopID = request.form["stop"]
		rating = request.form["rating"]
		username = request.form["username"]
		password = request.form["password"]

		r = requests.get(url="http://users:5000/verify_user/{}".format(username), json={"password": password}).json()

		if r["status"] == "success":
			ratingVars = {
				"stopID": stopID,
				"rating": rating,
				"username": username
			}

			r2 = requests.post(url="http://ratings:5000/rate_stop", json=ratingVars).json()

			if r2["status"] == "success":
				flash(message=r2["message"], category="success")
				return render_template('lineStops.html', stop_rating_form=StopLineRatingForm())
			else:
				flash(message=r2["message"], category="error")
				return render_template('lineStops.html', stop_rating_form=stop_rating_form)				

		flash(message=r["message"], category="error")
		return render_template('lineStops.html', stop_rating_form=stop_rating_form)

	else:
		return render_template('lineStops.html', stop_rating_form=stop_rating_form)

@app.route('/rateAllStops', methods=['GET', 'POST'])
def rateStopAll():
	stop_rating_form = StopAllRatingForm(request.form)

	requestedStops = requests.get(url="http://delijnapi:5000/stops").json()["stops"]
	stopchoices = []
	for s in requestedStops:
		stopchoices.append((str(s["id"]), "{}: {} - {}".format(s["id"], s["description"], s["townDescription"])))
	stop_rating_form.fillStops(stopchoices)

	if stop_rating_form.validate_on_submit():
		stopID = request.form["stop"]
		rating = request.form["rating"]
		username = request.form["username"]
		password = request.form["password"]

		r = requests.get(url="http://users:5000/verify_user/{}".format(username), json={"password": password}).json()

		if r["status"] == "success":
			ratingVars = {
				"stopID": stopID,
				"rating": rating,
				"username": username
			}

			r2 = requests.post(url="http://ratings:5000/rate_stop", json=ratingVars).json()

			if r2["status"] == "success":
				flash(message=r2["message"], category="success")
				return render_template('allStops.html', stop_rating_form=StopAllRatingForm())
			else:
				flash(message=r2["message"], category="error")
				return render_template('allStops.html', stop_rating_form=stop_rating_form)				

		flash(message=r["message"], category="error")
		return render_template('allStops.html', stop_rating_form=stop_rating_form)

	else:
		return render_template('allStops.html', stop_rating_form=stop_rating_form)

@app.route('/rateTownStops', methods=['GET', 'POST'])
def rateStopTown():
	stop_rating_form = StopTownRatingForm(request.form)

	if request.method == "POST":
		townID = stop_rating_form.town.data

		requestedStops = requests.get(url="http://delijnapi:5000/towns/{}".format(townID)).json()["stops"]
		stopchoices = []
		for s in requestedStops:
			stopchoices.append((str(s["id"]), "{}: {} - {}".format(s["id"], s["id"], s["description"])))
		stop_rating_form.fillStops(stopchoices)

	if stop_rating_form.validate_on_submit():
		stopID = request.form["stop"]
		rating = request.form["rating"]
		username = request.form["username"]
		password = request.form["password"]

		r = requests.get(url="http://users:5000/verify_user/{}".format(username), json={"password": password}).json()

		if r["status"] == "success":
			ratingVars = {
				"stopID": stopID,
				"rating": rating,
				"username": username
			}

			r2 = requests.post(url="http://ratings:5000/rate_stop", json=ratingVars).json()

			if r2["status"] == "success":
				flash(message=r2["message"], category="success")
				return render_template('townStops.html', stop_rating_form=StopTownRatingForm())
			else:
				flash(message=r2["message"], category="error")
				return render_template('townStops.html', stop_rating_form=stop_rating_form)				

		flash(message=r["message"], category="error")
		return render_template('townStops.html', stop_rating_form=stop_rating_form)

	else:
		return render_template('townStops.html', stop_rating_form=stop_rating_form)


@app.route('/getLinesForProvince/<province>')
def getLinesForProvince(province):
	url = apiURLs["lines"].format(provinceNumber=province)
	apiData = requests.get(url=url).json()
	return apiData

@app.route('/getLineDirections/<province>/<line>')
def getLineDirections(province, line):
	url = apiURLs["directions"].format(provinceNumber=province, lineNumber=line)
	apiData = requests.get(url=url).json()
	return apiData


if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)