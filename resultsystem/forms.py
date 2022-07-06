from wsgiref.validate import validator
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length



class AdminLoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(min=2, max=20)])
    password = PasswordField('password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit =SubmitField('Login')

# class AddStudentForm(FlaskForm):
#     rollno = IntegerField('Roll number of Student', validators=[DataRequired()])
#     name = StringField('Name For Student', validators=[DataRequired()])
#     email = StringField('Email For Student', validators=[DataRequired()])
#     mobileno = StringField('Mobile number of Student For Student', validators=[DataRequired()])
#     science = IntegerField('Science marks of Student', validators=[DataRequired()])
#     english = IntegerField('English marks of Student', validators=[DataRequired()])
#     math = IntegerField('Math marks of Student', validators=[DataRequired()])
#     submit =SubmitField('Add Student')

class DelForm(FlaskForm):
    rollno = IntegerField('Roll no. of Student remove')
    submit =SubmitField('Delete')
