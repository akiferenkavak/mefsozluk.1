# app/routes/main.py
from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.entry import Title, Entry
from sqlalchemy import desc
from app.models.entry import Entry, Title # Eğer Title da kullanılıyorsa


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    
    # Son entry zamanına göre başlıkları sırala
    titles = Title.query.order_by(desc(Title.last_entry_time)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('main/index.html', titles=titles, Entry=Entry)

@bp.route('/title/<int:id>')
def view_title(id):
    title = Title.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    
    entries = Entry.query.filter_by(title_id=id).order_by(Entry.created_at).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('main/title.html', title=title, entries=entries)

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('main/search.html', titles=[], query='')
    
    titles = Title.query.filter(Title.name.contains(query)).all()
    return render_template('main/search.html', titles=titles, query=query)