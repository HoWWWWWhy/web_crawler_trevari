from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class SearchForm(FlaskForm):
    book_title = StringField('읽을거리 제목', validators=[DataRequired()])
    submit = SubmitField('Search')
