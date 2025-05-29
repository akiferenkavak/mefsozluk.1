# app/models/user.py
from datetime import datetime, timezone
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import secrets
from app.models.social import Follow

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    real_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Email doğrulama
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmation_token = db.Column(db.String(100), unique=True)
    
    # Kullanıcı bilgileri
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Biyografi
    bio = db.Column(db.Text)
    
    # İlişkiler
    entries = db.relationship('Entry', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    # Takip sistemi
    following = db.relationship('Follow', 
                               foreign_keys='Follow.follower_id',
                               backref='follower', 
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    
    followers = db.relationship('Follow',
                               foreign_keys='Follow.followed_id',
                               backref='followed',
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    
    # Favori sistemi
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Mesaj sistemi
    sent_messages = db.relationship('Message',
                                   foreign_keys='Message.sender_id',
                                   backref='sender',
                                   lazy='dynamic',
                                   cascade='all, delete-orphan')
    
    received_messages = db.relationship('Message',
                                       foreign_keys='Message.recipient_id',
                                       backref='recipient',
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self):
        self.email_confirmation_token = secrets.token_urlsafe(32)
        return self.email_confirmation_token
    
    def can_create_title(self):
        """Yeni kullanıcı başlık açabilir mi kontrolü"""
        if self.is_admin:
            return True
        
        # self.created_at'in offset-aware (UTC) olduğundan emin olalım
        # Veritabanından okunurken timezone bilgisi kaybolmuş olabilir
        if self.created_at.tzinfo is None:
            # Eğer naive ise, UTC olarak varsay ve aware yap
            created_at_aware = self.created_at.replace(tzinfo=timezone.utc)
        else:
            # Zaten aware ise (örneğin PostgreSQL gibi bir DB kullanılıyorsa ve doğru ayarlandıysa),
            # olduğu gibi kullan veya UTC'ye normalize et (eğer farklı bir tz ise)
            # Ancak sizin default'unuz UTC olduğu için bu senaryoda tzinfo'su varsa UTC'dir.
            created_at_aware = self.created_at.astimezone(timezone.utc) # Farklı bir aware tz ise UTC'ye çevirir.

        current_time_utc = datetime.now(timezone.utc)
        days_since_creation = (current_time_utc - created_at_aware).days
        
        return days_since_creation >= current_app.config['NEW_USER_WAIT_DAYS']
    
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
    
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
    
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    
    def get_unread_message_count(self):
        return self.received_messages.filter_by(is_read=False).count()
    
    def __repr__(self):
        return f'<User {self.nickname}>'