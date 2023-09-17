import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
# Config Flask-email with Google Gmail Server
MAIL_SERVER = str(os.environ.get('MAIL_SERVER'))
MAIL_PORT = int(os.environ.get('MAIL_PORT'))
MAIL_USERNAME = str(os.environ.get('MAIL_USERNAME'))
MAIL_PASSWORD = str(os.environ.get('MAIL_PASSWORD'))
MAIL_USE_TLS = False
MAIL_USE_SSL = True
# MongoDB config
MONGODB_URI = os.environ.get('MONGO_URI')
