# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from app.models.user import User
from app.models.entry import Title, Entry
from app.utils.decorators import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # İstatistikler
    total_users = User.query.count()
    total_titles = Title.query.count()
    total_entries = Entry.query.count()
    pending_users = User.query.filter_by(email_confirmed=False).count()
    
    # Son eklenen kullanıcılar
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Son eklenen başlıklar
    recent_titles = Title.query.order_by(Title.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_titles': total_titles,
        'total_entries': total_entries,
        'pending_users': pending_users
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users,
                         recent_titles=recent_titles)

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    if search:
        query = query.filter(
            User.nickname.contains(search) | 
            User.email.contains(search) |
            User.real_name.contains(search)
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)

@bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Admin kullanıcı devre dışı bırakılamaz'})
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'aktif' if user.is_active else 'pasif'
    return jsonify({'success': True, 'message': f'Kullanıcı {status} hale getirildi'})

@bp.route('/user/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Kullanıcı admin yapıldı'})

@bp.route('/titles')
@login_required
@admin_required
def manage_titles():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Title.query
    if search:
        query = query.filter(Title.name.contains(search))
    
    titles = query.order_by(Title.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/titles.html', titles=titles, search=search)

@bp.route('/title/<int:title_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_title(title_id):
    title = Title.query.get_or_404(title_id)
    
    # Önce tüm entry'leri sil
    Entry.query.filter_by(title_id=title_id).delete()
    
    # Sonra başlığı sil
    db.session.delete(title)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Başlık ve tüm entry\'leri silindi'})