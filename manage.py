import os
import unittest

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app import models

# initialize the app with all its configurations
app = create_app(config_name=os.getenv("FLASK_ENV"))
migrate = Migrate(app, db)

# instance of class that will handle all our commands
manager = Manager(app)

# define migration command
manager.add_command("db", MigrateCommand)

# define our command for testing
@manager.command
def test():
	"""
	Run unit tests
	"""
	tests = unittest.TestLoader().discover("./tests", pattern="test*.py")
	result = unittest.TextTestRunner(verbosity=2).run(tests)
	if result.wasSuccessful():
		return 0
	return 1


if __name__ == '__main__':
	manager.run()

