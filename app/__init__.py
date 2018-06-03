from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, abort, make_response

from instance.config import app_config

# initialize db
db = SQLAlchemy()

def create_app(config_name):

	from app.models import Bucketlist, User

	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile("config.py")
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	db.init_app(app)

	"""
	Create bucketlist
	"""
	@app.route("/bucketlists/", methods=["POST"])
	def create_bucketlist():
		headers = request.headers.get('Authorization')
		token = headers.split(" ")[1]
		
		if token:
			user_id = User.decode_token(token)
			if not isinstance(user_id, str):
				if request.json:
					name = request.json.get('name', '')
					bucketlist = Bucketlist(name=name, created_by=user_id)
					bucketlist.save()
					response = jsonify({
						"id": bucketlist.id,
						"name": bucketlist.name,
						"date_created": bucketlist.date_created,
						"date_modified": bucketlist.date_modified,
						"created_by": user_id
					})
					response.status_code = 201
					return response
				else:
					abort(400)
			else:
				response = { "message": user_id }
				return make_response(jsonify(response)), 401
		else:
			return make_response(jsonify({"message": "Register to acquire your token for access."})), 401

	"""
	GET bucketlists
	"""
	@app.route("/bucketlists/", methods=["GET"])
	def get_bucketlists():
		headers = request.headers.get('Authorization')
		token = headers.split(" ")[1]

		user_id = User.decode_token(token)

		if not isinstance(user_id, str):
			bucketlists = Bucketlist.query.filter_by(created_by=user_id)
			results = []

			for bucketlist in bucketlists:
				obj = {
					"id": bucketlist.id,
					"name": bucketlist.name,
					"date_created": bucketlist.date_created,
					"date_modified": bucketlist.date_modified
				}
				results.append(obj)
			response = jsonify(results)
			response.status_code = 200
			return response
		else:
			response = { "message": user_id }
			return make_response(jsonify(response)), 401

	"""
	GET a bucketlist
	"""
	@app.route("/bucketlists/<int:id>/", methods=["GET"])
	def get_bucketlist(id):
		headers = request.headers.get('Authorization')
		token = headers.split(" ")[1]

		user_id = User.decode_token(token)

		if not isinstance(user_id, str):
			bucketlist = Bucketlist.query.filter_by(id=id).first()

			if not bucketlist:
				abort(404)

			response = jsonify({
				"id": bucketlist.id,
				"name": bucketlist.name,
				"date_created": bucketlist.date_created,
				"date_modified": bucketlist.date_modified,
				"created_by": bucketlist.created_by
			})
			response.status_code = 200
			return response
		else:
			response = { "message": user_id }
			return make_response(jsonify(response)), 401

	"""
	Edit a bucketlist
	"""
	@app.route("/bucketlists/<int:id>/", methods=["PUT"])
	def bucketlist_manupulation(id, **kwargs):
		headers = request.headers.get('Authorization')
		token = headers.split(" ")[1]

		user_id = User.decode_token(token)

		if not isinstance(user_id, str):
			if request.json:
				bucketlist = Bucketlist.query.filter_by(id=id).first()

				if not bucketlist:
					abort(404)

				name = request.json.get('name', '')
				bucketlist.name = name
				bucketlist.save()
				response = jsonify({
					"id": bucketlist.id,
					"name": bucketlist.name,
					"date_created": bucketlist.date_created,
					"date_modified": bucketlist.date_modified
				})
				response.status_code = 200
				return response
			else:
				abort(400)
		else:
			make_response(jsonify({"message": user_id})), 401

	"""
	DELETE bucketlist
	"""
	@app.route("/bucketlists/<int:id>/", methods=["DELETE"])
	def delete_bucketlist(id):
		headers = request.headers.get('Authorization')
		token = headers.split(" ")[1]

		user_id = User.decode_token(token)

		if not isinstance(user_id, str):
			bucketlist = Bucketlist.query.filter_by(id=id).first()

			bucketlist.delete()
			return make_response(jsonify({"message": "Bucketlist {} deleted successfully".format(bucketlist.id)})), 200
		else:
			return make_response(jsonify({"message": user_id})), 401

	@app.errorhandler(404)
	def not_found(error):
		return make_response(jsonify({"error": "Not Found"})), 404

	@app.errorhandler(400)
	def bad_request(error):
		return make_response(jsonify({"error": "Invalid request"})), 400

	from .auth import auth_blueprint
	app.register_blueprint(auth_blueprint)

	return app
