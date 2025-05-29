# app/routes/user.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.entry import Entry
from app.models.social import Follow, Message, Favorite
from app.forms import MessageForm, ProfileForm
from datetime import datetime, timezone
from sqlalchemy import desc, or_

bp = Blueprint('user', __name__)

@bp.route('/profile/<nickname>')
def profile(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    
    # Kullanıcının entry'leri
    entries = Entry.query.filter_by(author_id=user.id)\
                   .order_by(desc(Entry.created_at))\
                   .paginate(page=page, per_page=10, error_out=False)
    
    # İstatistikler
    total_entries = Entry.query.filter_by(author_id=user.id).count()
    total_favorites = Favorite.query.join(Entry)\
                              .filter(Entry.author_id == user.id).count()
    follower_count = user.followers.count()
    following_count = user.following.count()
    
    stats = {
        'total_entries': total_entries,
        'total_favorites': total_favorites,
        'follower_count': follower_count,
        'following_count': following_count
    }
    
    return render_template('user/profile.html', 
                         user=user, 
                         entries=entries, 
                         stats=stats)

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.real_name = form.real_name.data
        current_user.bio = form.bio.data
        db.session.commit()
        
        flash('Profil başarıyla güncellendi!')
        return redirect(url_for('user.profile', nickname=current_user.nickname))
    
    # Form verilerini doldur
    form.real_name.data = current_user.real_name
    form.bio.data = current_user.bio
    
    return render_template('user/edit_profile.html', form=form)

@bp.route('/follow/<nickname>', methods=['POST'])
@login_required
def follow_user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    
    if user == current_user:
        return jsonify({'success': False, 'message': 'Kendini takip edemezsin'})
    
    if current_user.is_following(user):
        return jsonify({'success': False, 'message': 'Zaten takip ediyorsun'})
    
    current_user.follow(user)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{user.nickname} takip edildi',
        'follower_count': user.followers.count()
    })

@bp.route('/unfollow/<nickname>', methods=['POST'])
@login_required
def unfollow_user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    
    if not current_user.is_following(user):
        return jsonify({'success': False, 'message': 'Zaten takip etmiyorsun'})
    
    current_user.unfollow(user)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{user.nickname} takipten çıkarıldı',
        'follower_count': user.followers.count()
    })

@bp.route('/following/<nickname>')
def following(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    following_users = User.query.join(Follow, User.id == Follow.followed_id)\
                               .filter(Follow.follower_id == user.id)\
                               .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('user/following.html', 
                         user=user, 
                         users=following_users, 
                         title='Takip Edilenler')

@bp.route('/followers/<nickname>')
def followers(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    follower_users = User.query.join(Follow, User.id == Follow.follower_id)\
                              .filter(Follow.followed_id == user.id)\
                              .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('user/followers.html', 
                         user=user, 
                         users=follower_users, 
                         title='Takipçiler')

@bp.route('/messages')
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    
    # Gelen mesajlar
    messages = Message.query.filter_by(recipient_id=current_user.id)\
                           .order_by(desc(Message.created_at))\
                           .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/messages.html', messages=messages)

@bp.route('/messages/sent')
@login_required
def sent_messages():
    page = request.args.get('page', 1, type=int)
    
    # Gönderilen mesajlar
    messages = Message.query.filter_by(sender_id=current_user.id)\
                           .order_by(desc(Message.created_at))\
                           .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/sent_messages.html', messages=messages)

@bp.route('/send-message/<nickname>', methods=['GET', 'POST'])
@login_required
def send_message(nickname):
    recipient = User.query.filter_by(nickname=nickname).first_or_404()
    
    if recipient == current_user:
        flash('Kendine mesaj gönderemezsin.')
        return redirect(url_for('user.profile', nickname=nickname))
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            subject=form.subject.data,
            content=form.content.data
        )
        
        db.session.add(message)
        db.session.commit()
        
        flash(f'{recipient.nickname} kullanıcısına mesaj gönderildi!')
        return redirect(url_for('user.profile', nickname=nickname))
    
    return render_template('user/send_message.html', form=form, recipient=recipient)

@bp.route('/message/<int:id>')
@login_required
def view_message(id):
    message = Message.query.get_or_404(id)
    
    # Sadece gönderen veya alan kişi görebilir
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        flash('Bu mesajı görme yetkiniz yok.')
        return redirect(url_for('user.messages'))
    
    # Eğer mesajı alan kişiyse, okundu olarak işaretle
    if message.recipient_id == current_user.id and not message.is_read:
        message.mark_as_read()
        db.session.commit()
    
    return render_template('user/view_message.html', message=message)

@bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    
    # Kullanıcının favorilediği entry'ler
    favorites = Entry.query.join(Favorite)\
                          .filter(Favorite.user_id == current_user.id)\
                          .order_by(desc(Favorite.created_at))\
                          .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/favorites.html', entries=favorites)

@bp.route('/entries')
@login_required
def my_entries():
    page = request.args.get('page', 1, type=int)
    
    # Kullanıcının entry'leri
    entries = Entry.query.filter_by(author_id=current_user.id)\
                        .order_by(desc(Entry.created_at))\
                        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/my_entries.html', entries=entries)

@bp.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html')

@bp.route('/search-users')
def search_users():
    query = request.args.get('q', '')
    if not query:
        return render_template('user/search_users.html', users=[], query='')
    
    users = User.query.filter(
        or_(
            User.nickname.contains(query),
            User.real_name.contains(query)
        )
    ).filter(User.is_active == True).limit(20).all()
    
    return render_template('user/search_users.html', users=users, query=query)