# app/routes/entry.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.entry import Title, Entry
from app.models.social import Favorite
from app.forms import TitleForm, EntryForm
from datetime import datetime, timezone

bp = Blueprint('entry', __name__)

@bp.route('/create-title', methods=['GET', 'POST'])
@login_required
def create_title():
    if not current_user.can_create_title():
        flash('Başlık açmak için daha fazla beklemeniz gerekiyor.')
        return redirect(url_for('main.index'))
    
    form = TitleForm()
    if form.validate_on_submit():
        # Başlık zaten var mı kontrol et
        existing_title = Title.query.filter_by(name=form.name.data).first()
        if existing_title:
            flash('Bu başlık zaten mevcut.')
            return redirect(url_for('main.view_title', id=existing_title.id))
        
        title = Title(name=form.name.data)
        db.session.add(title)
        db.session.commit()
        
        flash('Başlık başarıyla oluşturuldu!')
        return redirect(url_for('entry.add_entry', title_id=title.id))
    
    return render_template('entry/create_title.html', form=form)

@bp.route('/add/<int:title_id>', methods=['GET', 'POST'])
@login_required
def add_entry(title_id):
    title = Title.query.get_or_404(title_id)
    
    form = EntryForm()
    if form.validate_on_submit():
        entry = Entry(
            content=form.content.data,
            title_id=title_id,
            author_id=current_user.id
        )
        
        # Başlığın son entry zamanını güncelle
        title.update_last_entry_time()
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Entry başarıyla eklendi!')
        return redirect(url_for('main.view_title', id=title_id))
    
    return render_template('entry/add_entry.html', form=form, title=title)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    entry = Entry.query.get_or_404(id)
    
    if not entry.can_edit(current_user):
        flash('Bu entry\'yi düzenleme yetkiniz yok.')
        return redirect(url_for('main.view_title', id=entry.title_id))
    
    form = EntryForm()
    if form.validate_on_submit():
        entry.content = form.content.data
        entry.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        flash('Entry başarıyla güncellendi!')
        return redirect(url_for('main.view_title', id=entry.title_id))
    
    form.content.data = entry.content
    return render_template('entry/edit_entry.html', form=form, entry=entry)
