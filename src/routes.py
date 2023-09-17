from flask import render_template
from .requests import authenticate
from .requests.administrator import admin
from . import app


auth_route = authenticate
admin_route = admin

@app.route('/')
def home():
    return render_template('home.html', title="Home page")


# Api routes
from .api import bookings

booking = bookings
