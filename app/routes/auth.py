# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db, mail
from app.models.user import User
from app.forms import RegistrationForm, LoginForm
from flask_mail import Message

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            nickname=form.nickname.data,
            real_name=form.real_name.data
        )
        user.set_password(form.password.data)

        # Email doğrulama token'ı oluştur
        token = user.generate_confirmation_token()

        db.session.add(user)
        db.session.commit()

        # Doğrulama mailini gönder
        send_confirmation_email(user, token)

        flash('Kayıt başarılı! Lütfen email adresinizi kontrol edin ve hesabınızı doğrulayın.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            if not user.email_confirmed:
                flash('Lütfen önce email adresinizi doğrulayın.')
                return redirect(url_for('auth.login'))

            if not user.is_active:
                flash('Hesabınız devre dışı bırakılmış.')
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))

        flash('Geçersiz email veya şifre.')

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/confirm/<token>')
def confirm_email(token):
    user = User.query.filter_by(email_confirmation_token=token).first()
    if user:
        user.email_confirmed = True
        user.email_confirmation_token = None
        db.session.commit()
        flash('Email adresiniz başarıyla doğrulandı!')
    else:
        flash('Geçersiz doğrulama linki.')

    return redirect(url_for('auth.login'))

def send_confirmation_email(user, token):
    """Email doğrulama maili gönder"""
    msg = Message(
        subject='MEF Sözlük - Email Doğrulama',
        recipients=[user.email],
        html=f'''
        <h2>Hoş geldin {user.real_name}!</h2>
        <p>MEF Sözlük'e kaydınızı tamamlamak için aşağıdaki linke tıklayın:</p>
        <a href="{url_for('auth.confirm_email', token=token, _external=True)}">Hesabımı Doğrula</a>
        '''
    )
    mail.send(msg)