from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo, Optional, Length, NumberRange


class RegisterForm(FlaskForm):
    """Form to sign up new user"""

    username = StringField('Username', 
                        validators=[InputRequired(message='Username is required'),
                        Length(max=20, message='Username cannot be more than 20 characters')])

    email = StringField('Email', 
                        validators=[InputRequired(message='Email is required'),
                        Email(message='Must be valid email address'),
                        Length(max=30, message='Email address is too long.  Nobody wants all that in their address book')])

    first_name = StringField('First Name',
                        validators=[InputRequired(message='First name is required'),
                        Length(max=20, message='First Name is too long.  Get a nickname')])

    last_name = StringField('Last Name',
                        validators=[InputRequired(message='Last name is required'),
                        Length(max=20, message='Last Name is too long')])

    password = PasswordField('Password',
                        validators=[InputRequired(message='Password is required'),
                        EqualTo('confirm', message='Passwords must match')])

    confirm = PasswordField('Retype Password')


class LoginForm(FlaskForm):
    """Form to log in user"""

    username = StringField('Username', 
                        validators=[InputRequired(message='Username is required')])

    password = PasswordField('Password',
                        validators=[InputRequired(message='Password is required')])


class UserEditForm(FlaskForm):
    """Form to edit current user"""

    email = StringField('Email', 
                        validators=[Optional(strip_whitespace=True), 
                        Email(message='Must be valid email address')])

    bio = StringField('Bio')

    image_url = StringField('Profile Image URL')

    password = PasswordField('Current Password',
                        validators=[InputRequired(message='Password is required')])
    
    new_password = PasswordField('New Password',
                        validators=[EqualTo('confirm', message='Passwords must match')])

    confirm = PasswordField('Retype New Password')


class ReviewForm(FlaskForm):
    """Form to add or edit a game review"""

    title = StringField('Review Title',
                        validators=[InputRequired(message='Review must have a title'),
                        Length(min=3, max=50, message='Title must be between 3 and 50 characters in length')])

    rating = FloatField('Rating',
                        validators=[InputRequired(message='Must include a rating'),
                        NumberRange(min=0, max=10, message='Rating must be a number between 0 and 10')])

    text = TextAreaField('Review Text',
                        validators=[InputRequired(message='Review must include a review'),
                        Length(min=3, message='Review must be at least one word long')])

    
class QuestionForm(FlaskForm):
    """Form to ask or edit a question"""

    title = StringField('Question Title',
                        validators=[InputRequired(message='Question must have a title'),
                        Length(min=3, max=50, message='Title must be between 3 and 50 characters in length')])

    text = TextAreaField('Question Text',
                        validators=[InputRequired(message='Question is required'),
                        Length(min=3, message='Question must be at least one word long')])


class DeleteUserForm(FlaskForm):
    """Form to confirm user deletion"""

    password = PasswordField('Current Password',
                        validators=[InputRequired(message='Password is required')])