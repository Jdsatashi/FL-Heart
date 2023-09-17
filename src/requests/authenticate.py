from _datetime import datetime
import validators
from bson import ObjectId
from flask import render_template, redirect, request, flash, url_for, Blueprint, session
from src import mongodb
import bcrypt
from src.forms import RegisterForm, LoginForm
from .role import role_table

account_table = mongodb.mongo.get_collection('account')

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
        if account_table.find_one(username):
            flash(f"Username of Email.", "warning")
            return redirect(url_for('auth.register'))
        if account_table.find_one(emails):
            flash(f"Email {emails} was used.", "warning")
            return redirect(url_for('auth.register'))

        if form.validate_on_submit():
            account_table.insert_one({
                "username": username,
                "email": emails,
                "password": hashed_password,
                "role_id": role_auth_id,
                "created_at": datetime.utcnow(),
                "updated_at": None
            })
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
        user = account_table.find_one({
            "username": username
        })
        if form.validate_on_submit():
            if not user:
                flash(f"Username '{username}' is not found.", "warning")
                return redirect(url_for('auth.login'))
            if user and bcrypt.checkpw(password, user["password"]):
                is_role = user.get("role_id")
                if is_role is None:
                    account_table.find_one_and_update({
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
