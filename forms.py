# / Some of code has been copied from Corey Shaffer's flask application
# https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
# /

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextAreaField, SelectField
from wtforms.validators import DataRequired, length, Email, EqualTo, ValidationError
from flaskbb.models import User


class RegistrationFrom(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), length(min=4, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):

        user = User.query.filter_by(username=email.data).first()

        if user:
            raise ValidationError('That email is taken. Please choose a different one')


class LoginFrom(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Coursecopy(FlaskForm):
    Copy_type = SelectField(u'Copy Type', choices=[('0', 'Existing Courses'), ('1', 'New course')])
    Orig_courseId = StringField('Origin Course ID', validators=[validators.input_required()])
    Dest_courseId = TextAreaField('Destination Course IDs', validators=[validators.input_required()])
    submit = SubmitField('Submit')


class Coursemerge(FlaskForm):
    Course_id = StringField('Course ID', validators=[validators.input_required()])
    Course_name = StringField('Course Name', validators=[validators.input_required()])
    Child_courses = TextAreaField('Child Course IDs', validators=[validators.input_required()])
    submit = SubmitField('Submit')


class RequestRestForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError('There is no account with that email address')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
