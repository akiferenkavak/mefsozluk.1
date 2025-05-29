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
                         stats=stats,
                         timezone=timezone)

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
    # Profili görüntülenen kullanıcı (kimin takip ettiklerine bakıyoruz)
    profile_user = User.query.filter_by(nickname=nickname).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    # profile_user'ın takip ettiği kullanıcıların listesi
    # Follow.created_at olduğunu varsayıyorum, yoksa User.nickname'a göre sıralanabilir.
    following_pagination = User.query.join(Follow, User.id == Follow.followed_id)\
        .filter(Follow.follower_id == profile_user.id)\
        .order_by(desc(Follow.created_at)) \
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('user/following.html', 
                           profile_user=profile_user, # Kimin listesi olduğu bilgisi
                           users_page=following_pagination, # Takip edilen kullanıcıların paginated listesi
                           title=f"{profile_user.nickname} Takip Ettikleri",
                           timezone=timezone)

@bp.route('/followers/<nickname>')
def followers(nickname):
    # Profili görüntülenen kullanıcı (kimin takipçilerine bakıyoruz)
    profile_user = User.query.filter_by(nickname=nickname).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    # profile_user'ı takip eden kullanıcıların listesi
    # Follow.created_at olduğunu varsayıyorum
    followers_pagination = User.query.join(Follow, User.id == Follow.follower_id)\
        .filter(Follow.followed_id == profile_user.id)\
        .order_by(desc(Follow.created_at)) \
        .paginate(page=page, per_page=20, error_out=False)
        
    return render_template('user/followers.html', 
                           profile_user=profile_user, # Kimin listesi olduğu bilgisi
                           users_page=followers_pagination, # Takipçilerin paginated listesi
                           title=f"{profile_user.nickname} Takipçileri",
                           timezone=timezone)

@bp.route('/messages')
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    
    # Gelen mesajlar (değişken adını messages_pagination olarak değiştirdim 
    #                    Message model adıyla çakışmaması için)
    messages_pagination = Message.query.filter_by(recipient_id=current_user.id)\
                                  .order_by(desc(Message.created_at))\
                                  .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/messages.html', 
                           messages=messages_pagination, 
                           title="Gelen Mesajlarım",  # Sayfa başlığı eklendi
                           timezone=timezone)         # Timezone eklendi

@bp.route('/messages/sent')
@login_required
def sent_messages():
    page = request.args.get('page', 1, type=int)
    
    # Gönderilen mesajlar (değişken adını sent_messages_pagination olarak değiştirdim)
    sent_messages_pagination = Message.query.filter_by(sender_id=current_user.id)\
                                      .order_by(desc(Message.created_at))\
                                      .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/sent_messages.html', 
                           messages=sent_messages_pagination, 
                           title="Gönderilmiş Mesajlarım",  # Sayfa başlığı eklendi
                           timezone=timezone)             # Timezone eklendi
@bp.route('/send-message/<nickname>', methods=['GET', 'POST'])
@login_required
def send_message(nickname):
    recipient_user = User.query.filter_by(nickname=nickname).first_or_404() # recipient -> recipient_user olarak değiştirdim
    
    if recipient_user == current_user:
        flash('Kendine mesaj gönderemezsin.')
        return redirect(url_for('user.profile', nickname=nickname))
    
    form = MessageForm()
    
    # Formun recipient alanını GET isteğinde ve POST öncesi doldur
    # Bu, DataRequired doğrulamasını geçmesi için önemlidir.
    # Kullanıcı bu alanı görmeyecek ama formun bir parçası olacak.
    if request.method == 'GET':
        if request.args.get('subject'):
            form.subject.data = request.args.get('subject')
    
    # Her durumda (GET veya POST) formun recipient alanını alıcının kullanıcı adıyla doldur
    # Eğer bu alan şablonda gizli olarak render edilecekse veya sadece validasyon içinse
    form.recipient.data = recipient_user.nickname 

    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_user.id, # recipient_user.id kullanılıyor
            subject=form.subject.data,
            content=form.content.data
        )
        # form.recipient.data burada kullanılmıyor, recipient_user kullanılıyor.
        db.session.add(message)
        db.session.commit()
        flash(f'{recipient_user.nickname} kullanıcısına mesaj gönderildi!', 'success')
        return redirect(url_for('user.profile', nickname=recipient_user.nickname))
    
    # Eğer validate_on_submit False ise, form hatalarını görmek için:
    # print(form.errors) # Bu satırı sunucu konsolunda hataları görmek için ekleyebilirsiniz.

    return render_template('user/send_message.html', 
                           title=f"{recipient_user.nickname} Kullanıcısına Mesaj Gönder",
                           form=form, 
                           recipient=recipient_user, # recipient_user şablona gönderiliyor
                           timezone=timezone)

@bp.route('/message/<int:id>')
@login_required
def view_message(id):
    message = Message.query.get_or_404(id)
    
    # Sadece gönderen veya alan kişi görebilir
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        flash('Bu mesajı görme yetkiniz yok.', 'warning') # Flash mesaj kategorisi eklendi
        return redirect(url_for('user.messages'))
    
    # Eğer mesajı alan kişiyse ve mesaj okunmamışsa, okundu olarak işaretle
    if message.recipient_id == current_user.id and not message.is_read:
        message.mark_as_read()
        db.session.commit()
    
    page_title = f"Mesaj: {message.subject}" if message.subject else "Mesaj Detayı"

    return render_template('user/view_message.html', 
                           message=message,
                           title=page_title,    # Sayfa başlığı eklendi
                           timezone=timezone)   # Timezone eklendi

@bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    
    # Kullanıcının favorilediği entry'leri, favoriye eklenme zamanına göre sıralı olarak al
    # Entry.query.join(...) ile doğrudan Entry nesnelerini çekiyoruz.
    favorited_entries_pagination = (
        Entry.query
        .join(Favorite, Favorite.entry_id == Entry.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(desc(Favorite.created_at))  # En son favorilenenler en üstte
        .paginate(page=page, per_page=10, error_out=False)
    )
        
    return render_template('user/favorites.html', 
                           entries=favorited_entries_pagination,  # Şablona 'entries' adıyla gönderiyoruz
                           title="Favorilerim",                   # Sayfa başlığı için
                           timezone=timezone)                     # Tarih formatlaması için

@bp.route('/entries')
@login_required
def my_entries():
    page = request.args.get('page', 1, type=int)
    
    # Kullanıcının entry'leri
    entries = Entry.query.filter_by(author_id=current_user.id)\
                        .order_by(desc(Entry.created_at))\
                        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/my_entries.html', entries=entries, timezone=timezone)

@bp.route('/settings')
@login_required
def settings():
    return render_template('user/settings.html')

@bp.route('/search-users', methods=['GET']) # GET metodunu belirtmek iyi bir pratik
def search_users():
    query = request.args.get('q', '').strip() # Baştaki/sondaki boşlukları temizle
    page_title = "Kullanıcı Ara"

    if not query:
        users = [] # Arama yapılmadıysa boş liste
    else:
        page_title = f"Arama Sonuçları: '{query}'"
        users = User.query.filter(
            User.is_active == True, # Aktif kullanıcıları filtrele
            or_(
                User.nickname.ilike(f"%{query}%"),  # Büyük/küçük harf duyarsız arama
                User.real_name.ilike(f"%{query}%")
            )
        ).limit(20).all()
    
    return render_template('user/search_users.html', 
                           users=users, 
                           query=query, 
                           title=page_title,
                           timezone=timezone) # Tarih formatlaması için tutarlılık (gerçi bu sayfada pek kullanılmıyor)