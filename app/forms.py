from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                    SelectField, DecimalField)
from wtforms.validators import DataRequired, ValidationError , Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators = [DataRequired()])
    last_name = StringField('Last Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired(),
                                Length(min=8, max=20, message="Password length within 8 and 20.")])
    password2 = PasswordField('Repeat Password', validators = [DataRequired(),
                                EqualTo('password', message="Passwords must match."),
                                Length(min=8, max=20, message="Password length within 8 and 20.")])
    submit = SubmitField('Register')

    def validate_email(self, email):
        email = User.query.filter_by(email = email.data).first()
        if email is not None:
            raise ValidationError('Please use a different email')

class EditProfileForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    first_name = StringField('First Name', validators = [DataRequired()])
    last_name = StringField('Last Name', validators = [DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            email = User.query.filter_by(email = self.email.data).first()
            if email is not None:
                raise ValidationError('Please use a different username.')

class ExpenseForm(FlaskForm):
    type = SelectField('Payment Type', choices =[('cash','cash'),('card','card')])
    amount = DecimalField('Amount ($)', validators = [DataRequired()])
    submit = SubmitField('Add')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators = [DataRequired(),
                            Length(min=8, max=20, message="Password length within 8 and 20.")])
    password2 = PasswordField('Repeat Password', validators = [DataRequired(),
                                EqualTo('password', message="Passwords must match."),
                                Length(min=8, max=20, message="Password length within 8 and 20.")])
    submit = SubmitField('Request Password Reset')

class DeleteEntryForm(FlaskForm):
    submit = SubmitField('X')
