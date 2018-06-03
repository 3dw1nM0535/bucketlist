from flask import Blueprint

# instance of blueprint that represent authentication blueprint
auth_blueprint = Blueprint("auth", __name__)

from . import views
