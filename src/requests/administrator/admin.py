from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from _datetime import datetime, timedelta

from src.api.bookings import complex_validate_datetime
from src.constant.http_status import HTTP_401_UNAUTHORIZED
from src.forms import BookingForm
from src.mongodb import BOOKING_TABLE
from bson import ObjectId

from src.requests.authenticate import admin_authorize

admin_routes = Blueprint('admin', __name__)
admin = admin_routes


@admin.route('/')
def index_admin():
    authorize = admin_authorize()
    print("Authorize has value is: " + authorize)
    if not authorize:
        print('This is: "admin unauthorized"')
        flash(f"Unauthorized.", "danger")
        return redirect(url_for('home'))
    print('Admin authorized acceptable!')
    return render_template('administrator/admin.html', title='Admin Dashboard')


@admin.route('/bookings/', methods=['GET'])
def booking_index_admin():
    authorize = admin_authorize()
    if not authorize:
        print('This is: "admin unauthorized"')
        flash(f"Unauthorized.", "danger")
        return redirect(url_for('home'))

    datebook = request.args.get('datebook')
    type_search = request.args.get('type_search')
    query_search = request.args.get('query_search')
    current_page = request.args.get('current')
    print('Current page = ')
    print(current_page)
    data_booking_date = BOOKING_TABLE.distinct('date')
    form = BookingForm()
    data = []

    # Sorting by current date
    date_unique = set()
    date_active = set()
    today = datetime.now().strptime(datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y')
    for b in data_booking_date:
        date_unique.add(b)
        date_obj = datetime.strptime(b, '%m/%d/%Y')
        if date_obj >= today:
            date_formatted = date_obj.strftime('%m/%d/%Y')
            date_active.add(date_formatted)
    date_unique = sorted(date_unique)
    date_active = sorted(date_active)

    # Pagination follow by date
    filter_date = date_active[0] if date_active else date_unique[-1]
    filter_date = date_unique[int(current_page)] if current_page else filter_date
    data_booking2 = BOOKING_TABLE.find({'date': filter_date}) if filter_date else BOOKING_TABLE.find()
    current_index = current_page if current_page is not None else date_unique.index(date_active[0])
    current_index = int(current_index)
    next_page = current_index + 1 if (current_index + 1) < len(date_unique) else None
    prev_page = current_index - 1 if (current_index - 1) >= 0 else None
    page_paginate = {
        'current_page': current_index,
        'next_page': next_page,
        'prev_page': prev_page
    }

    if request.method == 'GET':
        if datebook is not None:
            try:
                data_booking2 = BOOKING_TABLE.find({'date': datebook})
            except TypeError:
                data_booking2 = BOOKING_TABLE.find({'date': str(datebook)})
        if type_search and query_search is not None:
            data_booking2 = BOOKING_TABLE.find({type_search: {"$regex": query_search, "$options": "i"}})
        for booking in data_booking2:
            booking['_id'] = str(booking['_id'])
            data.append(booking)
        if len(data) == 0:
            flash(f"Not found.", "warning")
        return render_template(
            'administrator/booking/manage.html',
            title='Booking Management',
            bookings=data,
            date_unique=date_unique,
            paginating=page_paginate,
            form=form)


@admin.route('/booking/<string:_id>', methods=['POST'])
def booking_edit_admin(_id):
    form = BookingForm()
    if request.method == 'POST' and form.validate_on_submit():
        doctor = form.doctor.data
        date_booking = form.date.data.strftime('%m/%d/%Y')
        time_booking = form.time.data.strftime('%H:%M')
        notes = form.note.data
        _id = _id

        validate_date = complex_validate_datetime(form.date.data, form.time.data, False)
        if not validate_date:
            return redirect(url_for('admin.booking_index_admin'))

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
            return redirect(url_for('admin.booking_index_admin'))
    else:
        return redirect(url_for('admin.booking_index_admin', form=form))
