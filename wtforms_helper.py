from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, Email
from passlib.hash import pbkdf2_sha256
from elephantsql import *

def invalid_credentials(form, field):
  """ Email and password checker (form take care of the inputs from the class it was called) """
  email_entered=form.email.data
  password_entered=field.data # we call the function from password field

  #Check if credentials are valid
  user_object=User.query.filter_by(email=email_entered).first()
  if user_object is None:
    raise ValidationError("Email or password is incorrect")
  elif not pbkdf2_sha256.verify(password_entered, user_object.password):
    raise ValidationError("Email or password is incorrect")


class RegistrationForm(FlaskForm):
  """Registration form"""
  email=StringField('', 
                      validators=[InputRequired(message="Email required"),
                        Email(message="Invalid email address")])
  password=PasswordField('', validators=[InputRequired(message="Password required"),
  Length(min=4, max=25, message="Password must be between 4 and 25 character")])
  confirm_password=PasswordField('', validators=[InputRequired(message="Password required"),
          EqualTo('password', message="Passwords must match")])
  submit_button=SubmitField('Create')

  def validate_email(self, email):
    user_by_email = User.query.filter_by(email=email.data).first()
    if user_by_email:
        raise ValidationError("Email address already exists. Please choose a different one.")

class LoginForm(FlaskForm):
  """ Login form """
  email=StringField('email_label', 
        validators=[InputRequired(message="Email required"), Email(message="Invalid email address")])
  password=PasswordField('password_label',
        validators=[InputRequired(message="Password required"),
        invalid_credentials])
  submit_button=SubmitField('Login')

