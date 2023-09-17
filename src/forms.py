from flask_wtf import FlaskForm
from wtforms import (StringField, EmailField, PasswordField, SubmitField,
                     BooleanField, DateField, TimeField, TextAreaField)
from wtforms.validators import DataRequired, EqualTo, Length


class RegisterForm(FlaskForm):
    username = StringField("Name", validators=[Length(min=6), DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8), DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Name", validators=[Length(min=6), DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8), DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Register")


class BookingForm(FlaskForm):
    doctor = StringField("Doctor", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    note = TextAreaField("Note")
    submit = SubmitField()
