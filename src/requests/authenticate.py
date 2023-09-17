from _datetime import datetime
import validators
from bson import ObjectId
from flask import render_template, redirect, request, flash, url_for, Blueprint, session, jsonify
from src.mongodb import ACCOUNT_TABLE
import bcrypt
from src.forms import RegisterForm, LoginForm
from .role import role_table
from ..constant.http_status import HTTP_401_UNAUTHORIZED

auth = Blueprint('auth', __name__)

role = role_table.find_one({'role': 'auth_user'})
role_auth_id = role['_id'] if role else role_table.find_one({'role': 'auth_user'})


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        username = form.username.data
        emails = form.email.data
        password = form.password.data.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        if not validators.email(emails):
            flash(f"Email was not valid.", "warning")
            return redirect(url_for('auth.register'))
        if ACCOUNT_TABLE.find_one({'username': username}):
            flash(f"Username was used.", "warning")
            return redirect(url_for('auth.register'))
        if ACCOUNT_TABLE.find_one({'email': emails}):
            flash(f"Email was used.", "warning")
            return redirect(url_for('auth.register'))

        if form.validate_on_submit():
            ACCOUNT_TABLE.insert_one({
                "username": username,
                "email": emails,
                "password": hashed_password,
                "role_id": role_auth_id,
                "created_at": datetime.utcnow(),
                "updated_at": None
            })
            session["username"] = username
            flash(f"Successfully registered! Welcome '{username}'.", "success")
            return redirect(url_for('home'))
    else:
        return render_template('auth/register.html', title='Register', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data.encode("utf-8")
        user = ACCOUNT_TABLE.find_one({
            "username": username
        })
        if form.validate_on_submit():
            if not user:
                flash(f"Username '{username}' is not found.", "warning")
                return redirect(url_for('auth.login'))
            if user and bcrypt.checkpw(password, user["password"]):
                is_role = user.get("role_id")
                if is_role is None:
                    ACCOUNT_TABLE.find_one_and_update({
                        '_id': ObjectId(user["_id"])
                    }, {
                        '$set': {
                            "role_id": role_auth_id
                        }
                    })
                session["username"] = username
                flash(f"Successfully registered! Welcome '{username}'.", "success")
                return redirect(url_for('home'))
            else:
                flash(f"Password was incorrect.", "danger")
                return redirect(url_for('auth.login'))
    else:
        return render_template('auth/login.html', title='Login', form=form)


@auth.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('home'))


def authorize_user():
    if 'username' in session:
        account_data = ACCOUNT_TABLE.find_one({'username': session['username']})
        account_data['_id'] = str(account_data['_id'])
        data = account_data
        if 'password' in data:
            data.pop('password')
        return data
    elif request.authorization["username"] is not None and request.authorization["password"] is not None:
        username = request.authorization["username"]
        password = request.authorization["password"]
        password_hash = password.encode('utf8')
        authorize = ACCOUNT_TABLE.find_one({
            'username': username,
        })
        authorize['_id'] = str(authorize['_id'])
        if bcrypt.checkpw(password_hash, authorize["password"]):
            data = authorize
            if 'password' in data:
                data.pop('password')
        else:
            return jsonify({
                'message': 'Wrong password'
            }), HTTP_401_UNAUTHORIZED
        return data
    else:
        return jsonify({'message': 'Unauthorized'}), HTTP_401_UNAUTHORIZED
