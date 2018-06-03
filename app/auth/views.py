from . import auth_blueprint

from flask import make_response, request, abort, jsonify
from flask.views import MethodView
from app.models import User

class RegistrationView(MethodView):
	"""
	This class registers a user
	"""
	def post(self):
		"""
		Handle post request
		"""
		user = User.query.filter_by(email=request.json.get('email')).first()

		if not user:
			# register user
			try:
				email = request.json.get('email')
				password = request.json.get('password')
				user = User(email=email, password=password)
				user.save()

				response = { "message": "You registered successfully. Please login." }
				return make_response(jsonify(response)), 201
			except Exception as e:
				# error occurred, return error as string
				response = { "message": str(e) }
				return make_response(jsonify(response)), 401
		else:
			# user already exists
			response = { "message": "User already exists. Please login." }
			return make_response(jsonify(response)), 202

class LoginView(MethodView):
	"""
	This class logs in a user
	"""
	def post(self):
		"""
		Handle post request
		"""
		try:
			# try to get user by their email address
			user = User.query.filter_by(email=request.json.get('email')).first()

			# validate user
			if user and user.validate_password(request.json.get('password')):
				# generate token
				token = user.generate_token(user.id)
				if token:
					response = {
						"message": "You logged in successfully.",
						"token": token.decode()
					}
					return make_response(jsonify(response)), 200
			else:
				response = { "message": "Invalid password or email. Please try again." }
				return make_response(jsonify(response)), 401
		except Exception as e:
			response = { "message": str(e) }
			return make_response(jsonify(response)), 500

# Define the API resource
registration_view = RegistrationView.as_view("register_view")
login_view = LoginView.as_view("login_view")

auth_blueprint.add_url_rule(
	"/auth/register/",
	view_func=registration_view,
	methods=["POST"]
)

auth_blueprint.add_url_rule(
	"/auth/login/",
	view_func=login_view,
	methods=["POST"]
)
