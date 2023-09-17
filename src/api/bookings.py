from datetime import datetime

import bcrypt
from bson import ObjectId
from flask import request, Blueprint, session, jsonify

from src.mongodb import BOOKING_TABLE, ACCOUNT_TABLE
from ..constant.http_status import *
from ..requests.authenticate import authorize_user

api_booking = Blueprint('bookings', __name__)


@api_booking.route('/', methods=['GET'])
def index_bookings():
    if 'username' in session:
        authorize = ACCOUNT_TABLE.find_one({
            'username': session['username'],
        })
        authorize['_id'] = str(authorize['_id'])
        return jsonify({
            "message": "Test this one",
        }), HTTP_200_OK
    elif request.authorization["username"] is not None and request.authorization["password"] is not None:
        username = request.authorization["username"]
        password = request.authorization["password"]
        password_hash = password.encode('utf8')
        authorize = ACCOUNT_TABLE.find_one({
            'username': username,
        })
        authorize['_id'] = str(authorize['_id'])
        if bcrypt.checkpw(password_hash, authorize["password"]):
            return jsonify({
                "message": "Test this one",
                "account_data": username,
                "password": password,
            }), HTTP_200_OK
    else:
        return jsonify({"message": "Wrong password"}), HTTP_401_UNAUTHORIZED


@api_booking.route('/create', methods=['POST', 'GET'])
def create_booking():
    if request.method == 'POST':
        user_data = authorize_user()
        email = user_data['email']
        doctor = request.get_json().get('doctor')
        date_booking = request.get_json().get('date')
        time_booking = request.get_json().get('time')
        notes = request.get_json().get('note')
        if not doctor or not date_booking or not time_booking:
            return jsonify({'error': 'Missing required fields'}), HTTP_400_BAD_REQUEST
        try:
            date_obj = datetime.strptime(date_booking, '%m/%d/%Y')
            date_formatted = date_obj.strftime('%m/%d/%Y')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        booking_conflict = BOOKING_TABLE.find_one({'doctor': doctor, 'date': date_booking, 'time': time_booking})
        if booking_conflict:
            return jsonify({'error': 'Booking was existed'}), HTTP_409_CONFLICT

        store_booking = BOOKING_TABLE.insert_one({
            'doctor': doctor,
            'date': date_formatted,
            'time': time_booking,
            'note': notes,
            'user_booking': email,
            'created_at': datetime.utcnow(),
            'updated_at': None
        })

        data = BOOKING_TABLE.find_one({
            'doctor': doctor,
            'date': date_formatted,
            'time': time_booking,
        })
        data['_id'] = str(data['_id'])
        if store_booking:
            return jsonify({
                'message': 'Created booking.',
                'booking': data
            }), HTTP_201_CREATED
        else:
            return (jsonify({'message': 'Internal server error.'}),
                    HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'GET':
        return jsonify({'message': 'Get this one'}), HTTP_200_OK


@api_booking.route('/edit/<string:_id>', methods=['GET', 'POST', 'PUT', 'PATCH'])
def update_booking(_id):
    user_data = authorize_user()
    email = user_data['email']

    data_booking = BOOKING_TABLE.find_one({
        '_id': ObjectId(_id)
    })
    data_booking['_id'] = str(data_booking['_id'])
    if not data_booking:
        return jsonify({
            'message': 'Error 404, not found'
        }), HTTP_404_NOT_FOUND
    if request.method == 'GET':
        return jsonify({
            'message': 'Successfully get booking.',
            'booking': data_booking
        }), HTTP_200_OK
    elif request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
        doctor = request.get_json().get('doctor')
        date_booking = request.get_json().get('date')
        time_booking = request.get_json().get('time')
        notes = request.get_json().get('note')

        if not doctor or not date_booking or not time_booking:
            return jsonify({'error': 'Missing required fields'}), HTTP_400_BAD_REQUEST

        try:
            date_obj = datetime.strptime(date_booking, '%m/%d/%Y')
            date_formatted = date_obj.strftime('%m/%d/%Y')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        edit_booking = BOOKING_TABLE.find_one_and_update({
            '_id': ObjectId(_id)}, {
            '$set': {
                'doctor': doctor,
                'date': date_formatted,
                'time': time_booking,
                'note': notes,
                'updated_at': datetime.utcnow()
            }
        })
        data_update = BOOKING_TABLE.find_one({
            '_id': ObjectId(_id)
        })
        data_update['_id'] = str(data_booking['_id'])
        if edit_booking:
            return jsonify({
                'message': 'Update booking.',
                'booking': data_update
            }), HTTP_200_OK
        else:
            return (jsonify({'message': 'Internal server error.'}),
                    HTTP_500_INTERNAL_SERVER_ERROR)


@api_booking.route('/delete/<string:_id>')
def delete_booking(_id):
    data_booking = BOOKING_TABLE.find_one({
        '_id': ObjectId(_id)
    })
    if not data_booking:
        return jsonify({
            'message': 'Error 404, not found'
        }), HTTP_404_NOT_FOUND
    deleting_booking = BOOKING_TABLE.find_one_and_delete({'_id': ObjectId(_id)})
    if deleting_booking:
        return jsonify({'message': 'Deleted successfully.'}), HTTP_200_OK
    return jsonify({'message': 'Error during handle deleting.'}), HTTP_400_BAD_REQUEST
