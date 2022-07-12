from wsgiref.validate import validator
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length
class AdminLoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(min=2, max=20)])
    password = PasswordField('password',validators=[DataRequired()])
    submit =SubmitField('Login')
