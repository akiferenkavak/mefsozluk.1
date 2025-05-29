# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mefsozluk.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail ayarları
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # MEF mail domain kontrolü
    ALLOWED_EMAIL_DOMAIN = 'mef.edu.tr'
    
    # Entry düzenleme süresi (dakika)
    ENTRY_EDIT_TIME_LIMIT = 15
    
    # Yeni üye başlık açma bekleme süresi (gün)
    NEW_USER_WAIT_DAYS = 7