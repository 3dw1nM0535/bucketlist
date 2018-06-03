import unittest
import os
import json
from app import create_app, db

class BucketlistTest(unittest.TestCase):
	"""
	Bucketlist test cases
	"""
	def setUp(self):
		"""
		Initialize setup variables
		"""
		self.app = create_app("testing")
		self.client = self.app.test_client

		# bind app to current context
		with self.app.app_context():
			# create all tables
			db.create_all()

	def register_user(self, email="user@email.com", password="9031"):
		"""
		Helper function to register user
		"""
		return self.client().post("/auth/register/", json=dict(email=email, password=password))

	def login_user(self, email="user@email.com", password="9031"):
		"""
		Helper function to login user
		"""
		return self.client().post("/auth/login/", json=dict(email=email, password=password))

	def test_api_can_create_bucketlist(self):
		"""
		Test API can create bucketlist(POST request)
		"""
		self.register_user()
		result = self.login_user()
		token = json.loads(result.data.decode())["token"]

		res = self.client().post(
			"/bucketlists/", 
			headers=dict(Authorization="Bearer " + token),
			json=dict(name="Practice TDD")
		)
		self.assertEqual(res.status_code, 201)
		self.assertIn("Practice", str(res.data))

	def test_api_can_return_all_bucketlists(self):
		"""
		Test API can return all bucketlists(GET request)
		"""
		self.register_user()
		result = self.login_user()
		token = json.loads(result.data.decode())["token"]

		res = self.client().post(
			"/bucketlists/",
			headers=dict(Authorization="Bearer " + token),
			json=dict(name="Practice TDD")
		)
		self.assertTrue(res.status_code, 201)
		res = self.client().get("/bucketlists/", headers=dict(Authorization="Bearer " + token))
		self.assertTrue(res.status_code, 200)
		self.assertIn("Practice", str(res.data))

	def test_api_can_get_a_bucketlist_by_id(self):
		"""
		Test API can return a bucketlist by its id(GET request)
		"""
		self.register_user()
		result = self.login_user()
		token = json.loads(result.data.decode())["token"]

		res = self.client().post(
			"/bucketlists/", 
			headers=dict(Authorization="Bearer " + token),
			json=dict(name="Practice TDD")
		)
		self.assertTrue(res.status_code, 201)
		result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
		result = self.client().get(
			"/bucketlists/{}/".format(result_in_json["id"]), 
			headers=dict(Authorization="Bearer " + token)
		)
		self.assertEqual(result.status_code, 200)
		self.assertIn("Practice", str(result.data))

	def test_api_can_edit_bucketlist(self):
		"""
		Test API can edit bucketlist(PUT request)
		"""
		self.register_user()
		result = self.login_user()
		token = json.loads(result.data.decode())["token"]

		res = self.client().post(
			"/bucketlists/",
			headers=dict(Authorization="Bearer " + token),
			json=dict(name="Eat, pray, and love")
		)
		self.assertEqual(res.status_code, 201)
		res = self.client().put(
			"/bucketlists/1/", 
			headers=dict(Authorization="Bearer " + token),
			json=dict(name="Don't just Eat, also pray, and love")
		)
		self.assertEqual(res.status_code, 200)
		result = self.client().get("/bucketlists/1/", headers=dict(Authorization="Bearer " + token))
		self.assertEqual(result.status_code, 200)
		self.assertIn("Don't just Eat", str(result.data))

	def test_api_can_delete_bucketlist(self):
		"""
		Test API can delete bucketlist(DELETE request)
		"""
		self.register_user()
		result = self.login_user()
		token = json.loads(result.data.decode())["token"]

		res = self.client().post(
			"/bucketlists/",
			headers=dict(Authorization="Bearer " + token),
			json=dict(name="Eat, pray, and love")
		)
		self.assertEqual(res.status_code, 201)
		result = self.client().delete("/bucketlists/1/", headers=dict(Authorization="Bearer " + token))
		self.assertEqual(result.status_code, 200)
		# Test if bucketlist exists, should return 404
		item = self.client().get("/bucketlists/1/", headers=dict(Authorization="Bearer " + token))
		self.assertEqual(item.status_code, 404)

	def tearDown(self):
		"""
		Tear down all initialized variables
		"""
		with self.app.app_context():
			# drop all database tables
			db.session.remove()
			db.drop_all()

if __name__ == '__main__':
	unittest.main()
