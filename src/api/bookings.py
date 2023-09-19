from datetime import datetime, timedelta, time

import bcrypt
from bson import ObjectId
from flask import request, Blueprint, session, jsonify, flash, redirect, url_for

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
    user_data = authorize_user()
    if not user_data:
        return jsonify({'message': 'Unauthorized'}), HTTP_401_UNAUTHORIZED

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
            return jsonify({'error': 'Invalid date format, format should be {"mm/dd/YY"}'}), HTTP_400_BAD_REQUEST

        try:
            time_obj = datetime.strptime(time_booking, '%H:%M:%S')
            time_formatted = time_obj.strftime('%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid time format, format should be {"HH:MM:SS"}'}), HTTP_400_BAD_REQUEST

        # validate datetime
        validate_datetime_json(date_obj, time_booking)

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
        validate_date_time(date_booking, time_booking)

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
        validate_datetime_json(date_obj, time_booking)

        booking_conflict = BOOKING_TABLE.find({'doctor': doctor, 'date': date_formatted, 'time': time_formatted})
        if booking_conflict:
            try:
                print(len(booking_conflict))
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


def validate_date_time(date, timeset):
    today = datetime.now().strptime(datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y')
    date_str = date.strftime('%d/%m/%Y')
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    time_obj = datetime.strptime(timeset.strftime('%H:%M'), '%H:%M').time()
    if date_obj < today:
        flash(f"Cannot booking past date.", "warning")
        return redirect((url_for('admin.booking_index_admin')))
    # T2 = 0, T3 = 1, T4 = 2, T5 = 3, T6 = 4, T7 = 5
    if date_obj.weekday() not in range(0, 5):
        flash(f"Cannot booking at Saturday and Sunday.", "warning")
        return redirect((url_for('admin.booking_index_admin')))
    if date_obj == today:
        # Time booking validates
        current_time = datetime.now().time()
        two_hours_delta = timedelta(hours=2)
        two_hours_from_now = (datetime.combine(datetime.today(), current_time) + two_hours_delta).time()
        if time_obj < two_hours_from_now:
            flash(f"You have to booking at least 2 hours from now.", "warning")
            return redirect((url_for('admin.booking_index_admin')))
    business_hours_start = datetime.strptime('08:00', '%H:%M').time()
    business_hours_end = datetime.strptime('16:00', '%H:%M').time()

    if time_obj == datetime.strptime('12:00', '%H:%M').time():
        flash(f"You cannot break time 12:00.", "warning")
        return redirect((url_for('admin.booking_index_admin')))
    elif time_obj < business_hours_start or time_obj > business_hours_end:
        flash(f"Booking is only allowed business hours (08:00 to 16:00).", "warning")
        return redirect((url_for('admin.booking_index_admin')))

def validate_datetime_json(date_obj, time_obj):
    # Validate datetime
    date_obj_validate = datetime.strptime(date_obj.strftime('%d/%m/%Y'), '%d/%m/%Y')
    today = datetime.now().strptime(datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y')
    time_obj_validate = datetime.strptime(time_obj, '%H:%M:%S').time()
    current_time = datetime.now().time()
    if date_obj_validate < today:
        return jsonify({
            'message': 'Cannot chose past date.'
        }), HTTP_400_BAD_REQUEST
    # T2 = 0, T3 = 1, T4 = 2, T5 = 3, T6 = 4, T7 = 5
    elif date_obj_validate.weekday() not in range(0, 4):
        return jsonify({
            'message': 'Cannot booking at Saturday and Sunday.'
        }), HTTP_400_BAD_REQUEST
    elif date_obj_validate == today:
        # Time booking validates
        print('This loop ok')
        two_hours_delta = timedelta(hours=2)
        two_hours_from_now = (datetime.combine(datetime.today(), current_time) + two_hours_delta).time()
        if time_obj_validate < two_hours_from_now:
            return jsonify({
                'message': 'You have to booking at least 2 hours from now.'
            })
    business_hours_start = datetime.strptime('08:00', '%H:%M').time()
    business_hours_end = datetime.strptime('16:00', '%H:%M').time()

    if time_obj_validate == datetime.strptime('12:00:00', '%H:%M:%S').time():
        return jsonify({
            'message': 'Booking at 12:00 is not allowed.'
        }), HTTP_400_BAD_REQUEST
    elif time_obj_validate < business_hours_start or time_obj_validate > business_hours_end:
        return jsonify({
            'message': 'Booking is only allowed business hours (08:00 to 16:00).'
        }), HTTP_400_BAD_REQUEST
