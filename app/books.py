from models import db, Book, Genre
from flask import Blueprint, render_template, request, flash, redirect, url_for
from tools import ImageSaver
from sqlalchemy.exc import IntegrityError

bp = Blueprint('book', __name__, url_prefix='/book')

BOOKS_PARAMS = [
    'name', 'short_desc', 'year', 'author', 'publisher', 'volume'
]

def params():
    return { p: request.form.get(p) or None for p in BOOKS_PARAMS }

@bp.route('/add')
def new():
    genres = list(item.name for item in db.session.execute(db.select(Genre)).scalars().all())
    return render_template('book_add.html', genres_list=genres)

@bp.route('/add', methods=['POST'])
def add():
    f = request.files.get('background_img')
    img = None
    book = Book()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()
        image_id = img.id if img else None
        book = Book(**params(), cover_id=image_id)
        db.session.add(book)
        db.session.commit()
    except IntegrityError as err:
        print(f'\n\n{err}\n\n')
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        db.session.rollback()
        genres = list(item.name for item in db.session.execute(db.select(Genre)).scalars().all())
        return render_template('book_add.html', genres_list=genres)

    flash('Книга была успешно добавлена!', 'success')

    return redirect(url_for('index')) # перенаправить на страницу просмотра данных о книге

@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()

        for key, value in params().items():
            setattr(book, key, value)

        db.session.commit()

        flash(f'Внесенные изменения были успешно добавлены!', 'success')
        return redirect(url_for('index'))

    book = Book.query.filter_by(id=book_id).first()

    genres = list()

    for item in db.session.execute(db.select(Genre)).scalars().all():
        genres.append(item.name)

    return render_template('book_edit.html', book=book, genres_list=genres)