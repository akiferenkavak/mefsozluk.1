# app/models/entry.py
from datetime import datetime, timezone
from app import db

class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # En son entry zamanı (sıralama için)
    last_entry_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    entries = db.relationship('Entry', backref='title', lazy='dynamic', cascade='all, delete-orphan')
    
    def entry_count(self):
        return self.entries.count()
    
    def update_last_entry_time(self):
        """Yeni entry eklendiğinde son entry zamanını güncelle"""
        self.last_entry_time = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<Title {self.name}>'

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Favori sistemi
    favorites = db.relationship('Favorite', backref='entry', lazy='dynamic', cascade='all, delete-orphan')
    
    def can_edit(self, user):
        """Entry düzenlenebilir mi kontrolü"""
        if user.is_admin:
            return True
        
        if self.author_id != user.id:
            return False
        
        # 15 dakika içinde düzenlenebilir
        edit_time_limit = 15 * 60  # saniye
        time_passed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return time_passed <= edit_time_limit
    
    def favorite_count(self):
        return self.favorites.count()
    
    def is_favorited_by(self, user):
        if not user.is_authenticated:
            return False
        return self.favorites.filter_by(user_id=user.id).first() is not None
    
    def __repr__(self):
        return f'<Entry {self.id} by {self.author.nickname}>'