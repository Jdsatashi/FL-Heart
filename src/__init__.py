from flask import Flask
from flask import render_template
from flask_mail import Mail, Message
from .constant.config import *

app = Flask(__name__)
# Config flask app
app.config.from_mapping(
    SECRET_KEY=SECRET_KEY,
    # Config Flask-email with Google Gmail Server
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_USE_TLS=MAIL_USE_TLS,
    MAIL_USE_SSL=MAIL_USE_SSL,
)


from src import mongodb

mail = Mail(app)

from .requests.role import add_default_role

add_default_role()
# Add all routes
from . import routes


# Register prefix routes
app.register_blueprint(routes.auth_route.auth, url_prefix='/auth')

# Register prefix api routes
app.register_blueprint(routes.booking.api_booking, url_prefix='/api/v1/bookings')
app.register_blueprint(routes.admin_route.admin_routes, url_prefix='/admin/management')

def sending_email(receivers):
    for receiver in receivers:
        msg = Message('Hello', sender='jdsatashi@gmail.com', recipients=[receiver])
        msg.html = render_template('email/email_template.html', receiver="John")
        mail.send(msg)
