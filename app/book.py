import bleach
from tools import ImageSaver
from auth import permission_check
from flask_login import current_user
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from models import db, Book, Genre, LinkTableBookGenre, Review
from flask import Blueprint, render_template, request, flash, redirect, url_for

bp = Blueprint('book', __name__, url_prefix='/book')

BOOKS_PARAMS = [
    'name', 'short_desc', 'year', 'author', 'publisher', 'volume'
]

def params():
    return { p: request.form.get(p) or None for p in BOOKS_PARAMS }

def insert_data_into_table_book_genres(book, choice_genres):
    db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book.id).delete()

    for genre_id in choice_genres:
        book_genre = LinkTableBookGenre(book_id=book.id, genre_id=genre_id)
        db.session.add(book_genre)

@bp.route('/new')
@login_required
@permission_check('add')
def new():
    genres = list(item for item in db.session.execute(db.select(Genre)).scalars().all())
    return render_template('book_add.html', genres_list=genres)

@bp.route('/add', methods=['POST'])
@login_required
@permission_check('add')
def add():
    genres = list(item for item in db.session.execute(db.select(Genre)).scalars().all())
    f = request.files.get('background_img')
    img = None

    if any(value == None for value in params().values()):
        flash(f'Заполните все поля', 'warning')
        return render_template('book_add.html', genres_list=genres)

    if f and f.filename:
        img = ImageSaver(f).create_file_data()
    else:
        flash(f'Загрузите обложку для книги', 'warning')
        return render_template('book_add.html', genres_list=genres)
    
    genres_from_form = request.form.getlist('genres_filter')
    
    if genres_from_form[0] == 'default':
        flash('Выберите жанр(ы) для книги', 'warning')
        return render_template('book_add.html', genres_list=genres)
    else:
        choice_genres = list(map(int, request.form.getlist('genres_filter')))
    
    book = Book(**params(), cover_id=img.id)
    book.short_desc = bleach.clean(book.short_desc)

    try:
        db.session.add(book)

        insert_data_into_table_book_genres(book, choice_genres)

        db.session.commit()

        if ImageSaver(f).download(img):
            flash('Книга была успешно добавлена!', 'success')
            return redirect(url_for('book.show', book_id=book.id))
        else:
            flash('Возникла ошибка при загрузке обложки', 'danger')
            return render_template('book_add.html', genres_list=genres)
        
    except IntegrityError:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        db.session.rollback()
        return render_template('book_add.html', genres_list=genres)
    
@bp.route('/<int:book_id>/show', methods=['GET', 'POST'])
def show(book_id):
    book = db.session.query(Book).filter(Book.id == book_id).first()

    reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()

    # исключение на то, если пользователь AnonimousUserMixin, т.к. у анонимного юзера нет свойства current_user
    try:
        can_write_review = not bool(db.session.query(Review).filter(Review.user_id == current_user.id).first())
    except AttributeError:
        can_write_review = False

    try:
        average_score = sum(review.mark for review in reviews_list) / len(reviews_list)
    except ZeroDivisionError:
        average_score = 0

    return render_template(
        'show.html',
        book=book,
        reviews_list=reviews_list,
        average_score=average_score,
        number_of_reviews=len(reviews_list),
        can_write_review=can_write_review
    )

@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_check('edit')
def edit(book_id):
    book = Book.query.filter_by(id=book_id).first()

    genres = list(item for item in db.session.execute(db.select(Genre)).scalars().all())

    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()

        genres_from_form = request.form.getlist('genres_filter')
    
        if genres_from_form[0] == 'default':
            flash('Выберите жанр(ы) для книги', 'warning')
            return render_template('book_edit.html', genres_list=genres, book=book)
        else:
            choice_genres = list(map(int, request.form.getlist('genres_filter')))

        try:
            insert_data_into_table_book_genres(book, choice_genres)
            db.session.commit()
        except IntegrityError:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            db.session.rollback()
            return render_template('book_edit.html', genres_list=genres, book=book)

        for key, value in params().items():
            if key == 'short_desc' and value is not None:
                setattr(book, key, bleach.clean(value))
            elif value is not None:
                setattr(book, key, value)

        db.session.commit()

        flash(f'Внесенные изменения были успешно добавлены!', 'success')
        return redirect(url_for('index'))

    return render_template(
        'book_edit.html', 
        book=book, 
        genres_list=genres
    )

@bp.route('/<int:book_id>/review_add', methods=['GET', 'POST'])
@login_required
def review_add(book_id):
    if request.method == 'POST':
        if db.session.query(Review).filter(Review.user_id == current_user.id).first():
            flash('Вы уже оставляли рецензию на эту книгу.', 'warning')
            return redirect(url_for('book.show', book_id=book_id))

        text = request.form['text']
        mark = bleach.clean(request.form['mark'])
        
        try:
            db.session.add(
                Review(mark=mark, text=text, book_id=book_id, user_id=current_user.id)
            )
            db.session.commit()
            return redirect(url_for('book.show', book_id=book_id))
        except IntegrityError:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            db.session.rollback()
            return render_template('review_add.html', book_id=book_id)

    book = db.session.query(Book).filter(Book.id == book_id).first()

    return render_template('review_add.html', book=book)