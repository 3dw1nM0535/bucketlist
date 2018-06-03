import unittest
import json
from app import create_app, db

class AuthCase(unittest.TestCase):
	"""
	Test Authentication blueprint
	"""
	def setUp(self):
		"""
		Initialize all variables
		"""
		self.app = create_app(config_name="testing")
		self.client = self.app.test_client

		with self.app.app_context():
			# create all tables
			db.session.close()
			db.drop_all()
			db.create_all()

	def test_user_registration(self):
		"""
		Test API can register user
		"""
		res = self.client().post("/auth/register/", json=dict(email="milly@gmail.com", password="1234"))
		# get results in json format
		result = json.loads(res.data.decode())
		self.assertEqual(res.status_code, 201)
		self.assertEqual(str(result["message"]), "You registered successfully. Please login.")

	def test_already_registered_user(self):
		"""
		Test API can't register user twice
		"""
		res = self.client().post("/auth/register/", json=dict(email="milly@gmail.com", password="1234"))
		self.assertEqual(res.status_code, 201)
		second_res = self.client().post("/auth/register/", json=dict(email="milly@gmail.com", password="1234"))
		self.assertEqual(second_res.status_code, 202)
		# get result in json format
		result = json.loads(second_res.data.decode())
		self.assertEqual(str(result["message"]), "User already exists. Please login.")

	def test_user_login(self):
		"""
		Test User can login
		"""
		res = self.client().post("/auth/register/", json=dict(email="mike@gmail.com", password="4747"))
		self.assertEqual(res.status_code, 201)
		login_res = self.client().post("/auth/login/", json=dict(email="mike@gmail.com", password="4747"))
		result = json.loads(login_res.data.decode())
		self.assertEqual(login_res.status_code, 200)
		self.assertEqual(result["message"], "You logged in successfully.")
		self.assertTrue(result["token"])

	def test_non_registered_users_cannot_login(self):
		"""
		Test Non-registered users cannot log in
		"""
		res = self.client().post("/auth/login/", json=dict(email="not_user@email.com", password="9031"))
		result = json.loads(res.data.decode())
		self.assertEqual(res.status_code, 401)
		self.assertEqual(result["message"], "Invalid password or email. Please try again.")
