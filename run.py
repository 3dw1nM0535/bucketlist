import os

from app import create_app

# get env(development/production/testing/staging)
config_name = os.getenv("FLASK_ENV")

# initialize app
app = create_app(config_name)

# make this file executable
if __name__ == '__main__':
	app.run()
