"""Forms for authentication module."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80),
        Regexp(r'^[\w.-]+$', message="Username can only contain letters, numbers, dots, and dashes")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128),
        Regexp(r'.*[A-Z].*', message="Password must contain at least one uppercase letter"),
        Regexp(r'.*[a-z].*', message="Password must contain at least one lowercase letter"),
        Regexp(r'.*[0-9].*', message="Password must contain at least one number"),
        Regexp(r'.*[!@#$%^&*()_+].*', message="Password must contain at least one special character")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class PasswordResetRequestForm(FlaskForm):
    """Form for requesting password reset."""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])

class PasswordResetForm(FlaskForm):
    """Form for resetting password."""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=128),
        Regexp(r'.*[A-Z].*', message="Password must contain at least one uppercase letter"),
        Regexp(r'.*[a-z].*', message="Password must contain at least one lowercase letter"),
        Regexp(r'.*[0-9].*', message="Password must contain at least one number"),
        Regexp(r'.*[!@#$%^&*()_+].*', message="Password must contain at least one special character")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
