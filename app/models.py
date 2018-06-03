from app import db
from flask_bcrypt import Bcrypt
from datetime import timedelta, datetime
import jwt
from flask import current_app

class User(db.Model):
	"""
	Rep user table
	"""
	___tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(256), nullable=False, unique=True)
	password = db.Column(db.String(256), nullable=False)
	bucketlists = db.relationship(
		'Bucketlist', order_by='Bucketlist.id', cascade='all, delete-orphan'
	)

	def __init__(self, email, password):
		"""
		Initialize variables
		"""
		self.email = email
		self.password = Bcrypt().generate_password_hash(password).decode()

	def validate_password(self, password):
		"""
		Validate user password
		"""
		return Bcrypt().check_password_hash(self.password, password)

	def generate_token(self, user_id):
		"""
		Generate token
		"""
		try:
			# setup payload with an expiration time
			payload = {
				"exp": datetime.utcnow() + timedelta(minutes=60),
				"iat": datetime.utcnow(),
				"sub": user_id
			}
			# create the byte string token using the payload and the secret key
			jwt_string = jwt.encode(
				payload,
				current_app.config.get("SECRET_KEY"),
				algorithm="HS256"
			)
			return jwt_string

		except Exception as e:
			# return error in string format if an error occurs
			return str(e)

	@staticmethod
	def decode_token(token):
		"""
		Decode access token from Authorization Header
		"""
		try:
			# try decoding token using SECRET_KEY
			payload = jwt.decode(token, current_app.config.get("SECRET_KEY"))
			return payload["sub"]
		except jwt.ExpiredSignatureError:
			# if token is expired return error string
			return "Exprired token. Please log in to get a new one."
		except jwt.InvalidTokenError:
			# if token is invalid, return error string
			return "Invalid token. Please register or log in."

	def save(self):
		"""
		Save user to database
		"""
		db.session.add(self)
		db.session.commit()

class Bucketlist(db.Model):
	"""
	Rep bucketlist table
	"""
	___tablename__ = "bucketlists"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(225))
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
	created_by = db.Column(db.Integer, db.ForeignKey(User.id))
	
	def __init__(self, name, created_by):
		self.name = name
		self.created_by = created_by

	def save(self):
		"""
		Saving bucketlist and updating bucketlist
		"""
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_all(user_id):
		"""
		Return bucketlist for a given user
		"""
		return Bucketlist.query.filter_by(created_by=user_id)

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def __repr__(self):
		return "<Bucketlist {}>".format(self.name)
