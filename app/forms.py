# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from app.utils.validators import validate_mef_email, validate_unique_email, validate_unique_nickname

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(), 
        validate_mef_email,
        validate_unique_email
    ])
    nickname = StringField('Kullanıcı Adı', validators=[
        DataRequired(), 
        Length(min=3, max=20),
        validate_unique_nickname
    ])
    real_name = StringField('Gerçek Adınız', validators=[
        DataRequired(), 
        Length(min=2, max=100)
    ])
    password = PasswordField('Şifre', validators=[
        DataRequired(), 
        Length(min=6)
    ])
    password2 = PasswordField('Şifre Tekrar', validators=[
        DataRequired(), 
        EqualTo('password')
    ])
    submit = SubmitField('Kayıt Ol')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class EntryForm(FlaskForm):
    content = TextAreaField('Entry', validators=[
        DataRequired(), 
        Length(min=10, max=5000)
    ])
    submit = SubmitField('Gönder')

class TitleForm(FlaskForm):
    name = StringField('Başlık', validators=[
        DataRequired(), 
        Length(min=3, max=200)
    ])
    submit = SubmitField('Başlık Aç')

class MessageForm(FlaskForm):
    recipient = StringField('Kime', validators=[DataRequired()])
    subject = StringField('Konu', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Mesaj', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Gönder')