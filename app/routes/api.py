# app/routes/api.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.entry import Entry
from app.models.social import Favorite

bp = Blueprint('api', __name__)

@bp.route('/favorite/<int:entry_id>', methods=['POST'])
@login_required
def toggle_favorite(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        entry_id=entry_id
    ).first()
    
    if favorite:
        # Favoriden çıkar
        db.session.delete(favorite)
        is_favorited = False
    else:
        # Favoriye ekle
        favorite = Favorite(user_id=current_user.id, entry_id=entry_id)
        db.session.add(favorite)
        is_favorited = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_favorited': is_favorited,
        'favorite_count': entry.favorite_count()
    })

@bp.route('/delete-entry/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(entry_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Yetkiniz yok'}), 403
    
    entry = Entry.query.get_or_404(entry_id)
    title_id = entry.title_id
    
    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Entry silindi'})