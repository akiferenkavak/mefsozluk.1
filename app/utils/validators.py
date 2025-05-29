# app/utils/validators.py
from wtforms.validators import ValidationError
from app.models.user import User
from config import Config

def validate_mef_email(form, field):
    """MEF email domain kontrolü"""
    if not field.data.endswith('@' + Config.ALLOWED_EMAIL_DOMAIN):
        raise ValidationError(f'Sadece @{Config.ALLOWED_EMAIL_DOMAIN} uzantılı email adresleri kabul edilir.')

def validate_unique_email(form, field):
    """Email benzersizlik kontrolü"""
    user = User.query.filter_by(email=field.data).first()
    if user:
        raise ValidationError('Bu email adresi zaten kullanılıyor.')

def validate_unique_nickname(form, field):
    """Nickname benzersizlik kontrolü"""
    user = User.query.filter_by(nickname=field.data).first()
    if user:
        raise ValidationError('Bu kullanıcı adı zaten alınmış.')