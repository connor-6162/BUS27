from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TaskForm(FlaskForm):
    name = StringField("Task name", validators=[DataRequired(), Length(max=200)])
    deadline = DateTimeLocalField("Deadline", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    submit = SubmitField("Add task")
