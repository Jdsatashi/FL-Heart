from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from _datetime import datetime, timedelta

from src.api.bookings import validate_date_time
from src.forms import BookingForm
from src.mongodb import BOOKING_TABLE
from bson import ObjectId


admin_routes = Blueprint('admin', __name__)
admin = admin_routes


@admin.route('/')
def index_admin():
    return render_template('administrator/admin.html', title='Admin Dashboard')


@admin.route('/bookings/', methods=['GET', 'POST'])
def booking_index_admin():
    data_booking = BOOKING_TABLE.find()
    form = BookingForm()
    data = []
    if request.method == 'GET':
        for booking in data_booking:
            booking['_id'] = str(booking['_id'])
            booking['created_at'] = str(booking['created_at'])
            data.append(booking)
        return render_template(
            'administrator/booking/manage.html',
            title='Booking Management',
            bookings=data,
            form=form)
    return render_template(
        'administrator/booking/manage.html',
        title='Booking Management',
        bookings=data,
        form=form,
        error_message='Invalid request.'
    )

@admin.route('/booking/<string:_id>', methods=['POST'])
def booking_edit_admin(_id):
    form = BookingForm()
    if request.method == 'POST' and form.validate_on_submit():
        doctor = form.doctor.data
        date_booking = form.date.data.strftime('%m/%d/%Y')
        time_booking = form.time.data.strftime('%H:%M')
        notes = form.note.data
        _id = _id

        validate_date_time(form.date.data, form.time.data)

        edit_booking = BOOKING_TABLE.find_one_and_update(
            {'_id': ObjectId(_id)},
            {
                '$set': {
                    'doctor': doctor,
                    'date': date_booking,
                    'time': time_booking,
                    'note': notes,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        if edit_booking:
            return redirect((url_for('admin.booking_index_admin')))
    else:
        return redirect((url_for('admin.booking_index_admin', form=form)))
