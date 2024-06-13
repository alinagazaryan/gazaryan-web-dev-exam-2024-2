import datetime, io
from models import db
from config import PER_PAGE
from models import History, Book
from sqlalchemy import func, desc
from auth import permission_check
from flask_login import login_required
from flask import Blueprint, render_template, request, send_file

bp = Blueprint('history', __name__, url_prefix='/history')

def make_file(data, fields):
    csv_content = '№,' + ','.join(fields) + '\n'
    for i, item in enumerate(data):
        values = [str(item.get(f, '')) for f in fields]
        csv_content += f'{i+1},' + ','.join(values) + '\n'
    f = io.BytesIO()
    f.write(csv_content.encode('utf-8'))
    f.seek(0)
    return f

@bp.route('/users_activity')
@login_required
@permission_check('check_logs')
def users_activity():
    records = History.query.order_by(History.created_at.desc())
    page = request.args.get('page', 1, type=int)

    pagination = records.paginate(page=page, per_page=PER_PAGE)
    records = pagination.items

    data = list()

    for record in records:
        data.append({
            'author': record.book.author,
            'name': record.book.name,
            'created_at': record.created_at
        })

        if record.user == None:
            data[len(data) - 1]['full_name'] = 'Неаутентифицированный пользователь'
        else:
            data[len(data) - 1]['full_name'] = record.user.full_name

    if request.args.get('download_csv_file'):
        f = make_file(data, ['full_name', 'author', 'name', 'created_at'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='users_activity.csv')

    return render_template(
        'history/users_activity.html',
        pagination=pagination,
        data=data
    )

@bp.route('/books_statistic', methods=['GET', 'POST'])
@login_required
@permission_check('check_logs')
def books_statistic():
    page = request.args.get('page', 1, type=int)

    records = History.query.with_entities(History.book_id, 
        func.count(History.book_id).label('count')).filter(
        History.user_id.isnot(-1)).group_by(
        History.book_id).order_by(desc('count'))

    if request.method == 'POST':
        date_from = request.form['date-from']
        date_to = request.form['date-to']

        if date_from:
            records = records.filter(History.created_at >= date_from)

        if date_to:
            date_to_next_day = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            records = records.filter(History.created_at <= date_to_next_day)

    pagination = records.paginate(page=page, per_page=PER_PAGE)
    records = pagination.items

    data = list()

    for book_id, count in records:
        book = db.session.query(Book).filter(Book.id == book_id).first()
        data.append({
            'author': book.author,
            'name': book.name,
            'count': count
        })

    if request.args.get('download_csv_file'):
        f = make_file(data, ['author', 'name', 'count'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='books_statistic.csv')

    return render_template(
        'history/books_statistic.html',
        pagination=pagination,
        data=data
    ) 