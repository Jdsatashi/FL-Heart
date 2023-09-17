from flask import redirect, request, Blueprint, session, jsonify
from bson import ObjectId
from _datetime import datetime
from src import mongodb
from .confirm_booking import store_confirm, confirm_table
from ..constant.http_status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_404_NOT_FOUND

booking_table = mongodb.mongo.get_collection('bookings')

api_booking = Blueprint('bookings', __name__)


@api_booking.route('/', methods=['GET'])
def index_bookings():
    return jsonify({
        "message": "Test this one"
    }), HTTP_200_OK


@api_booking.route('/create', methods=['POST', 'GET'])
def create_booking():
    if request.method == 'POST':
        doctor = request.get_json().get('doctor')
        date_booking = request.get_json().get('date')
        time_booking = request.get_json().get('time')
        notes = request.get_json().get('note')
        is_conflicted = None
        if not doctor or not date_booking or not time_booking:
            return jsonify({'error': 'Missing required fields'}), HTTP_400_BAD_REQUEST

        try:
            date_obj = datetime.strptime(date_booking, '%m/%d/%Y')
            date_formatted = date_obj.strftime('%m/%d/%Y')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        booking_conflict = booking_table.find_one({'doctor': doctor, 'date': date_booking, 'time': time_booking})
        if booking_conflict:
            is_conflicted = 'conflicted'
            booking_conflict['_id'] = str(booking_conflict['_id'])
            confirm_table.find_one_and_update({'booking_id': ObjectId(booking_conflict['booking_id'])}, {
                '$set': {
                    'is_conflicted': is_conflicted,
                }
            })

        store_booking = booking_table.insert_one({
            'doctor': doctor,
            'date': date_formatted,
            'time': time_booking,
            'note': notes,
            'created_at': datetime.utcnow(),
            'updated_at': None
        })

        data = booking_table.find_one({
            'doctor': ['doctor'],
            'date': ['date_formatted'],
            'time': ['time_booking'],
        })
        data['_id'] = str(data['_id'])
        store_confirm(data['_id'], is_conflicted)
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
    data_booking = booking_table.find_one({
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
        edit_booking = booking_table.find_one_and_update({
            '_id': ObjectId(_id)}, {
            '$set': {
                'doctor': doctor,
                'date': date_formatted,
                'time': time_booking,
                'note': notes,
                'updated_at': datetime.utcnow()
            }
        })
        data_update = booking_table.find_one({
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
    data_booking = booking_table.find_one({
        '_id': ObjectId(_id)
    })
    if not data_booking:
        return jsonify({
            'message': 'Error 404, not found'
        }), HTTP_404_NOT_FOUND
    deleting_booking = booking_table.find_one_and_delete({'_id': ObjectId(_id)})
    if deleting_booking:
        return jsonify({'message': 'Deleted successfully.'}), HTTP_200_OK
    return jsonify({'message': 'Error during handle deleting.'}), HTTP_400_BAD_REQUEST
