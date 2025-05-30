from app import db, create_app
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        email="admin@mef.edu.tr",
        nickname="admin",
        real_name="Admin Kullanıcı",
        password_hash=generate_password_hash("güçlüşifre"),
        is_admin=True,
        email_confirmed=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin kullanıcı eklendi.")