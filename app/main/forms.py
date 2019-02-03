from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField , PasswordField, SubmitField, ValidationError, TextAreaField,IntegerField,SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email,NumberRange
from .. import db
from ..models.users import User
import pandas as pd
from flask_ckeditor import CKEditorField



EqualTo('confirm', message='Passwords must match')

class SignUp(FlaskForm):

    username = StringField('Username: ' , validators= [Length(3,50), DataRequired()])
    Roll_no = IntegerField('Roll Number: ', validators = [DataRequired()])
    email = StringField('Email: ', validators= [Email()])
    
    password = PasswordField('Password: ' ,validators= [Length(3,50), DataRequired()])
    phone_number = IntegerField('Phone Number: ', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password: ' ,validators= [Length(3,50), DataRequired(), EqualTo('password', message='Passwords must match')])
    Submit = SubmitField('Sign Up !')

    def validate_username(self, username):

        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username Already Taken')
    def validate_email(self, email):

        email = User.query.filter_by(email = email.data).first()
        if email:
            raise ValidationError('Email Already in Use')

class Login(FlaskForm):

    email = StringField('Email: ', validators = [Email()])
    password = PasswordField('Password: ' ,validators= [Length(3,50), DataRequired()])
    remember = BooleanField('Remember Me')
    Submit = SubmitField('Login')

class Admin_editor(FlaskForm):
    
    username = StringField('Username: ' , validators= [Length(3,50), DataRequired()])
    email = StringField('Email: ', validators= [Email(),DataRequired()])
    role = StringField('Role: ', validators= [DataRequired()])
    Submit = SubmitField('Edit User')

class Profile_Edit(FlaskForm):
    
    username = StringField('Username' , validators= [Length(3,50), DataRequired()])
    email = StringField('Email', validators= [Email(),DataRequired()])
    about_me = TextAreaField('About Me')
    location = StringField('Location')
    Submit = SubmitField('Edit User')

# class PostForm(FlaskForm):
#     body = TextAreaField("What's on your mind?", validators=[DataRequired()])
#     submit = SubmitField('Post')


class PostForm(FlaskForm):
    title = StringField('Title')
    body = CKEditorField('Body') 
    submit = SubmitField('Submit')


    

  
    

    
    
    
    
