import os
from app import create_app, db
from app.models.user import User # User modelini import edin
from app.models.entry import Title, Entry # Title ve Entry modellerini import edin
from app.models.social import Follow, Favorite, Message # Social modellerini import edin

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Title': Title, 
        'Entry': Entry,
        'Follow': Follow,
        'Favorite': Favorite,
        'Message': Message
    }

if __name__ == '__main__':
    # Uygulama bağlamı içinde veritabanı tablolarını oluştur (eğer yoksa)
    # Production ortamında bu satır yerine migrations kullanmak daha iyidir.
    # Ancak Render'da ilk deploy için veya basit projelerde kullanılabilir.
    with app.app_context():
        db.create_all()

    # Render'ın sağladığı PORT ortam değişkenini kullan, yoksa varsayılan olarak 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Debug modunu app.config'den al, yoksa varsayılan olarak False (production için)
    # Lokal geliştirme için config.py'da DEBUG = True yapabilirsiniz.
    # Render'da DEBUG ortam değişkeni genellikle otomatik ayarlanır veya siz ayarlayabilirsiniz.
    debug_mode = app.config.get('DEBUG', os.environ.get('FLASK_DEBUG', '0') == '1')

    # Uygulamayı 0.0.0.0 host'unda ve belirlenen portta çalıştır
    app.run(host='0.0.0.0', port=port, debug=debug_mode)