from flask import Blueprint
from flask_restful import Api
from resources.Record import Record

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
api.add_resource(Record, 
# Post a new record
'/Record', 
# GET, PATCH or DELETE a record by ID
'/Record/<recordId>')
