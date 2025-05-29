from datetime import datetime, timezone
from flask import current_app # current_app'i import ediyoruz
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
        # Önce kullanıcı geçerli mi ve giriş yapmış mı kontrol edelim
        if not user or not user.is_authenticated:
            return False
            
        if user.is_admin:
            return True
        
        if self.author_id != user.id:
            return False
        
        # self.created_at'in offset-aware (UTC) olduğundan emin olalım
        # Veritabanından okunurken timezone bilgisi kaybolmuş olabilir
        if self.created_at.tzinfo is None:
            # Eğer naive ise, UTC olarak varsay ve aware yap
            created_at_aware = self.created_at.replace(tzinfo=timezone.utc)
        else:
            # Zaten aware ise, UTC'ye normalize et (farklı bir tz ise veya emin olmak için)
            # Sizin default'unuz UTC olduğu için bu genellikle zaten UTC'dir.
            created_at_aware = self.created_at.astimezone(timezone.utc)
        
        current_time_utc = datetime.now(timezone.utc)
        time_passed_seconds = (current_time_utc - created_at_aware).total_seconds()
        
        # Düzenleme süresi limitini config'den al (dakika cinsinden), saniyeye çevir
        # Config'de ENTRY_EDIT_TIME_LIMIT olarak tanımlı olduğunu varsayıyoruz
        edit_limit_minutes = current_app.config.get('ENTRY_EDIT_TIME_LIMIT', 15) # Varsayılan 15 dakika
        edit_limit_seconds = edit_limit_minutes * 60
        
        return time_passed_seconds <= edit_limit_seconds
    
    def favorite_count(self):
        return self.favorites.count()
    
    def is_favorited_by(self, user):
        if not user or not user.is_authenticated: # Kullanıcı kontrolü eklendi
            return False
        return self.favorites.filter_by(user_id=user.id).first() is not None
    
    def __repr__(self):
        # Yazarın olup olmadığını kontrol etmek daha güvenli olabilir, 
        # özellikle lazy loading veya silinme durumlarında
        author_nickname = self.author.nickname if self.author else "Bilinmeyen Yazar"
        return f'<Entry {self.id} by {author_nickname}>'
