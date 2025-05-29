# config.py
import os
from datetime import timedelta



class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mefsozluk.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail ayarları (Yandex için güncellendi)
    # Ortam değişkenleri ayarlanmamışsa varsayılan Yandex ayarları kullanılır.
    # MAIL_USERNAME, MAIL_PASSWORD ve MAIL_DEFAULT_SENDER için ortam değişkenlerini ayarlamanız GEREKİR.
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.yandex.com'
    # Yandex için varsayılan port 465 (SSL ile)
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    # Yandex SSL kullanır, bu nedenle True olmalı
    MAIL_USE_SSL = (os.environ.get('MAIL_USE_SSL') or 'True').lower() == 'true'
    # Yandex SSL kullanırken TLS genellikle False olur
    MAIL_USE_TLS = (os.environ.get('MAIL_USE_TLS') or 'False').lower() == 'true' 
    
    # BU ALANLARI ORTAM DEĞİŞKENLERİ İLE AYARLAMALISINIZ:
    # Örnek: export MAIL_USERNAME="hesabiniz@yandex.com"
    # Örnek: export MAIL_PASSWORD="yandex_uygulama_sifreniz"
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # MAIL_DEFAULT_SENDER ortam değişkeni ayarlanmamışsa, MAIL_USERNAME değeri kullanılır.
    # Örnek: export MAIL_DEFAULT_SENDER="gonderen_adresiniz@yandex.com" (isteğe bağlı, yoksa MAIL_USERNAME kullanılır)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    
    # MEF mail domain kontrolü
    ALLOWED_EMAIL_DOMAIN = 'mef.edu.tr'
    
    # Entry düzenleme süresi (dakika)
    ENTRY_EDIT_TIME_LIMIT = 15
    
    # Yeni üye başlık açma bekleme süresi (gün)
    NEW_USER_WAIT_DAYS = 0 # geçici olarak 0 yapıldı, test için. Üretimde 7 veya daha fazla olmalı.