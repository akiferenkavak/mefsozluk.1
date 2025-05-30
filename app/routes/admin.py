# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User 
from app.models.entry import Title, Entry # Title ve Entry modelleri aynı yerden import ediliyor
from app.utils.decorators import admin_required


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_titles = Title.query.count()
    total_entries = Entry.query.count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_titles = Title.query.order_by(Title.created_at.desc()).limit(5).all()
    recent_entries = Entry.query.order_by(Entry.created_at.desc()).limit(5).all()
    
    # total_favorites'ı da ekleyelim eğer Favorite modeliniz varsa
    try:
        from app.models.social import Favorite # Favorite modelinizin olduğu yeri varsayarak
        total_favorites = Favorite.query.count()
    except ImportError:
        total_favorites = None # Veya 0, veya stats'tan çıkarın

    stats = {
        'total_users': total_users,
        'total_titles': total_titles,
        'total_entries': total_entries,
    }
    if total_favorites is not None:
        stats['total_favorites'] = total_favorites
    
    return render_template('admin/dashboard.html', 
                           stats=stats, 
                           recent_users=recent_users,
                           recent_titles=recent_titles,
                           recent_entries=recent_entries)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', default="", type=str).strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # *** UnboundLocalError için DÜZELTME: query'nin başlangıç değeri burada atanmalı ***
    query = User.query 
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            User.nickname.ilike(search_term) | 
            User.email.ilike(search_term)
        )
    
    order_column_map = {
        'id': User.id,
        'nickname': User.nickname,
        'email': User.email,
        'is_active': User.is_active,
        'is_admin': User.is_admin,
        'created_at': User.created_at
    }
    order_column = order_column_map.get(sort_by, User.created_at)

    if sort_order == 'asc':
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
    
    users = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('admin/users.html', 
                           users=users, 
                           search=search, 
                           sort_by=sort_by, 
                           sort_order=sort_order)

@admin_bp.route('/user/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Kendinizi pasif yapamazsınız.'}), 403
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True, is_active=True).count()
        if user.is_active and admin_count <= 1 : # Aktif olan son admin pasif yapılamaz
             return jsonify({'success': False, 'message': 'Son aktif admin pasif yapılamaz.'}), 403
    user.is_active = not user.is_active
    db.session.commit()
    status_message = 'aktif hale getirildi' if user.is_active else 'pasif hale getirildi'
    return jsonify({'success': True, 'message': f'{user.nickname} kullanıcısı başarıyla {status_message}.', 'is_active': user.is_active})

@admin_bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id and user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            return jsonify({'success': False, 'message': 'Son adminin yetkisi kaldırılamaz.'}), 403
    user.is_admin = not user.is_admin
    db.session.commit()
    status_message = 'admin yapıldı' if user.is_admin else 'admin yetkisi kaldırıldı'
    return jsonify({'success': True, 'message': f'{user.nickname} kullanıcısı başarıyla {status_message}.', 'is_admin': user.is_admin})

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Kendinizi silemezsiniz.'}), 403
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
             return jsonify({'success': False, 'message': 'Son admin silinemez.'}), 403
    try:
        # İlişkili entry'leri anonim hale getirme veya silme (iş mantığınıza göre)
        # Entry.query.filter_by(author_id=user_id).update({Entry.author_id: None}) # Örnek
        # Veya sil: Entry.query.filter_by(author_id=user_id).delete()
        # Favorileri sil: Favorite.query.filter_by(user_id=user_id).delete()
        # Bu adımlar model ilişkilerinize ve cascade ayarlarınıza bağlıdır.
        # Eğer cascade ayarlarınız varsa, sadece user'ı silmek yeterli olabilir.
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'{user.nickname} adlı kullanıcı başarıyla silindi.'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Kullanıcı silinirken hata: {e}")
        return jsonify({'success': False, 'message': f'Kullanıcı silinirken bir hata oluştu: {str(e)}'}), 500

@admin_bp.route('/titles')
@login_required
@admin_required
def manage_titles():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', default="", type=str).strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    query = Title.query # BAŞLANGIÇ ATAMASI

    if search:
        search_term = f"%{search}%"
        query = query.filter(Title.name.ilike(search_term))
    
    order_column_map = {
        'id': Title.id,
        'name': Title.name,
        'entry_count': db.func.count(Entry.id), # Bu şekilde sıralama için join ve group_by gerekebilir
        'created_at': Title.created_at,
        'last_entry_time': Title.last_entry_time
    }
    # Entry sayısına göre sıralama daha karmaşıktır, şimdilik basit tutuyorum.
    # Eğer entry_count'a göre sıralamak isterseniz, subquery veya join/group_by kullanmanız gerekir.
    order_column = order_column_map.get(sort_by, Title.created_at)

    if sort_by == 'entry_count': # Özel durum: entry sayısına göre sıralama
        if sort_order == 'asc':
            query = query.outerjoin(Title.entries).group_by(Title.id).order_by(db.func.count(Entry.id).asc())
        else:
            query = query.outerjoin(Title.entries).group_by(Title.id).order_by(db.func.count(Entry.id).desc())
    elif sort_order == 'asc':
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
        
    titles = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/titles.html', 
                            titles=titles, 
                            search=search,
                            sort_by=sort_by,
                            sort_order=sort_order)

@admin_bp.route('/title/<int:title_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_title(title_id):
    title = Title.query.get_or_404(title_id)
    title_name = title.name
    try:
        # Modeldeki cascade='all, delete-orphan' sayesinde ilişkili entry'ler otomatik silinecektir.
        db.session.delete(title)
        db.session.commit()
        flash(f"'{title_name}' başlıklı konu ve tüm entry'leri başarıyla silindi.", 'success')
        return jsonify({'success': True, 'redirect': url_for('admin.manage_titles')})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Başlık silinirken hata: {e}")
        flash(f"'{title_name}' başlıklı konu silinirken bir hata oluştu.", 'danger')
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'}), 500

@admin_bp.route('/entries')
@login_required
@admin_required
def manage_entries():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', default="", type=str).strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')

    query = Entry.query # BAŞLANGIÇ ATAMASI
    
    # Join'leri arama veya sıralama için gerektiğinde ekle
    if search or sort_by in ['author_nickname', 'title_name']:
         query = query.join(User, Entry.author_id == User.id).join(Title, Entry.title_id == Title.id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Entry.content.ilike(search_term) |
            User.nickname.ilike(search_term) |
            Title.name.ilike(search_term)
        )
    
    order_column_map = {
        'id': Entry.id,
        'content': Entry.content, # Uzun metin için sıralama pratik olmayabilir
        'author_nickname': User.nickname,
        'title_name': Title.name,
        'created_at': Entry.created_at
    }
    order_column = order_column_map.get(sort_by, Entry.created_at)

    if sort_order == 'asc':
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
        
    entries = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/entries.html', 
                            entries=entries, 
                            search=search,
                            sort_by=sort_by,
                            sort_order=sort_order)

@admin_bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Entry başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Entry silinirken hata: {e}")
        flash(f'Entry silinirken bir hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_entries', 
                            page=request.args.get('page'), 
                            search=request.args.get('search'),
                            sort_by=request.args.get('sort_by'),
                            sort_order=request.args.get('sort_order')))