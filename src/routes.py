from flask import render_template, session, jsonify

from .mongodb import ACCOUNT_TABLE
from .requests import authenticate
from .requests.administrator import admin
from . import app
from .requests.role import role_admin_id

auth_route = authenticate
admin_route = admin

@app.route('/')
def home():
    if 'username' in session:
        account_data = ACCOUNT_TABLE.find_one({'username': session['username']})
        account_data['_id'] = str(account_data['_id'])
        data = account_data
        if 'password' in data:
            data.pop('password')
        data['role_id'] = str(data['role_id'])
        session['role_id'] = data['role_id']
    return render_template('home.html', title="Home page", admin_id=role_admin_id)


# Api routes
from .api import bookings

booking = bookings
