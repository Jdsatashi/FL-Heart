from flask import redirect, request, Blueprint, session, jsonify
from bson import ObjectId
from _datetime import datetime
from src import mongodb
from ..constant.http_status import HTTP_200_OK

confirm_table = mongodb.mongo.get_collection('confirmation')

api_confirm = Blueprint('confirm_booking', __name__)

@api_confirm.route('/', methods=['GET'])
def index_confirm():
    return jsonify({
        "message": "Test this one confirm"
    }), HTTP_200_OK

def store_confirm(_id, is_conflicted):
    confirm_table.insert_one({
        'status': 'waiting',
        'booking_id': _id,
        'is_conflicted': is_conflicted,
        'created_at': datetime.utcnow(),
        'updated_at': None
    })
