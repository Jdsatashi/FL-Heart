from datetime import datetime, timedelta, time

import bcrypt
import pymongo
from bson import ObjectId
from flask import request, Blueprint, session, jsonify, flash, redirect, url_for

from src.mongodb import BOOKING_TABLE, ACCOUNT_TABLE
from ..constant.http_status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from ..requests.authenticate import authorize_user

api_booking = Blueprint('bookings', __name__)


@api_booking.route('/', methods=['GET'])
def index_bookings():
    user_data = authorize_user()
    if not user_data:
        return jsonify({'message': 'Unauthorized'}), HTTP_401_UNAUTHORIZED
    if request.method == 'GET':
        booking_data = BOOKING_TABLE.find().sort([("date", pymongo.ASCENDING), ("time", pymongo.ASCENDING)])
        data = []
        for booking in booking_data:
            booking['_id'] = str(booking['_id'])
            data.append(booking)
        if not data:
            return jsonify({
                'message': 'Get booking data successfully!',
                "Booking list": data
            }), HTTP_200_OK
        return jsonify({
            'message': '404 not found'
        }), HTTP_404_NOT_FOUND

@api_booking.route('/create', methods=['POST', 'GET'])
def create_booking():
    user_data = authorize_user()
    if not user_data:
        return jsonify({'message': 'Unauthorized'}), HTTP_401_UNAUTHORIZED

    if request.method == 'POST':
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
            return jsonify({'error': 'Invalid date format, format should be {"mm/dd/YY"}'}), HTTP_400_BAD_REQUEST

        try:
            time_obj = datetime.strptime(time_booking, '%H:%M:%S')
            time_formatted = time_obj.strftime('%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid time format, format should be {"HH:MM:SS"}'}), HTTP_400_BAD_REQUEST

        # validate datetime
        validate_datetime = complex_validate_datetime(date_obj, time_booking, True)
        if validate_datetime is not None:
            return jsonify(validate_datetime), HTTP_400_BAD_REQUEST

        booking_conflict = BOOKING_TABLE.find_one({'doctor': doctor, 'date': date_formatted, 'time': time_formatted})
        if booking_conflict:
            return jsonify({'message': 'Booking was existed'}), HTTP_409_CONFLICT

        store_booking = BOOKING_TABLE.insert_one({
            'doctor': doctor,
            'date': date_formatted,
            'time': time_formatted,
            'note': notes,
            'user_booking': email,
            'created_at': datetime.utcnow(),
            'updated_at': None
        })

        data = BOOKING_TABLE.find_one({
            'doctor': doctor,
            'date': date_formatted,
            'time': time_formatted,
        })
        data['_id'] = str(data['_id'])
        if store_booking:
            return jsonify({
                'message': 'Created booking.',
                'booking': data,
            }), HTTP_201_CREATED
        else:
            return (jsonify({'message': 'Internal server error.'}),
                    HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'GET':
        return jsonify({'message': 'Get this one'}), HTTP_200_OK


@api_booking.route('/edit/<string:_id>', methods=['GET', 'POST', 'PUT', 'PATCH'])
def update_booking(_id):
    user_data = authorize_user()
    if not user_data:
        return jsonify({'message': 'Unauthorized'}), HTTP_401_UNAUTHORIZED

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
            return jsonify({'error': 'Invalid date format, format should be {"mm/dd/YY"}'}), HTTP_400_BAD_REQUEST
        try:
            time_obj = datetime.strptime(time_booking, '%H:%M')
            time_formatted = time_obj.strftime('%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid time format, format should be {"HH:MM:SS"}'}), HTTP_400_BAD_REQUEST

        # validate datetime
        validate_datetime = complex_validate_datetime(date_obj, time_booking, True)
        if validate_datetime is not None:
            return jsonify(validate_datetime), HTTP_400_BAD_REQUEST

        booking_conflict = BOOKING_TABLE.find({'doctor': doctor, 'date': date_formatted, 'time': time_formatted})
        if booking_conflict:
            try:
                for booking_data in booking_conflict:
                    booking_data['_id'] = str(booking_data['_id'])
                    if data_booking['_id'] == booking_conflict['_id']:
                        return jsonify({'message': 'Booking was existed'}), HTTP_409_CONFLICT
            except ValueError:
                booking_conflict['_id'] = str(booking_conflict['_id'])
                if data_booking['_id'] == booking_conflict['_id']:
                    return jsonify({'message': 'Booking was existed'}), HTTP_409_CONFLICT

        edit_booking = BOOKING_TABLE.find_one_and_update({
            '_id': ObjectId(_id)}, {
            '$set': {
                'doctor': doctor,
                'date': date_formatted,
                'time': time_formatted,
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
    user_data = authorize_user()
    if not user_data:
        return jsonify({'message': 'Unauthorized'}), HTTP_401_UNAUTHORIZED

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


def complex_validate_datetime(date_obj, time_obj, is_json: bool):
    today = datetime.now().strptime(datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y')
    date_obj_validate = datetime.strptime(date_obj.strftime('%d/%m/%Y'), '%d/%m/%Y')
    time_obj_validate = datetime.strptime(time_obj.strftime('%H:%M'), '%H:%M').time() if not is_json \
        else datetime.strptime(time_obj, '%H:%M:%S').time()
    current_time = datetime.now().time()
    if date_obj_validate < today:
        if is_json:
            return {'message': 'Cannot chose past date.'}
        flash(f"Cannot booking past date.", "warning")
        return False
    # T2 = 0, T3 = 1, T4 = 2, T5 = 3, T6 = 4, T7 = 5
    elif date_obj_validate.weekday() not in range(0, 5):
        if is_json:
            return {'message': 'Cannot booking at Saturday and Sunday.'}
        flash(f"Cannot booking at Saturday and Sunday.", "warning")
        return False
    elif date_obj_validate == today:
        # Time booking validates
        two_hours_delta = timedelta(hours=2)
        two_hours_from_now = (datetime.combine(datetime.today(), current_time) + two_hours_delta).time()
        if time_obj_validate < two_hours_from_now:
            if is_json:
                return {'message': 'You have to booking at least 2 hours from now.'}
            flash(f"You have to booking at least 2 hours from now.", "warning")
            return False
    business_hours_start = datetime.strptime('08:00', '%H:%M').time()
    business_hours_end = datetime.strptime('16:00', '%H:%M').time()
    breaking_hours = datetime.strptime('12:00', '%H:%M').time() if not is_json \
        else datetime.strptime('12:00:00', '%H:%M:%S').time()
    if time_obj_validate == breaking_hours:
        if is_json:
            return {'message': 'Booking at 12:00 is not allowed.'}
        flash(f"You cannot break time 12:00.", "warning")
        return False
    elif time_obj_validate < business_hours_start or time_obj_validate > business_hours_end:
        if is_json:
            return {'message': 'Booking is only allowed business hours (08:00 to 16:00).'}
        flash(f"Booking is only allowed business hours (08:00 to 16:00).", "warning")
        return False
