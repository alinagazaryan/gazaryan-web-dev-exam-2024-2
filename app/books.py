from models import db, Book, Genre
from flask import Blueprint, render_template, request, flash, redirect, url_for
from tools import ImageSaver
from sqlalchemy.exc import IntegrityError

bp = Blueprint('book', __name__, url_prefix='/book')

BOOKS_PARAMS = [
    'name', 'short_desc', 'year', 'author', 'publisher', 'volume'
]

# Функция для извлечения параметров из запроса
def params():
    # Возвращает словарь, где ключи - это параметры из BOOKS_PARAMS, а значения - данные из формы запроса
    return { p: request.form.get(p) or None for p in BOOKS_PARAMS }

# Маршрут для отображения формы добавления новой книги
@bp.route('/add')
def new():
    # Получение списка всех жанров из базы данных
    genres = list(item.name for item in db.session.execute(db.select(Genre)).scalars().all())
    # Рендеринг страницы добавления книги с переданным списком жанров
    return render_template('book_add.html', genres_list=genres)

# Маршрут для обработки формы добавления новой книги, поддерживающий метод POST
@bp.route('/add', methods=['POST'])
def add():
    # Получение файла изображения из формы запроса
    f = request.files.get('background_img')
    img = None  # Переменная для хранения объекта изображения
    book = Book()  # Создание пустого объекта книги
    try:
        # Если изображение было загружено
        if f and f.filename:
            img = ImageSaver(f).save()  # Сохранение изображения и создание соответствующего объекта
        image_id = img.id if img else None  # Получение идентификатора изображения, если оно было загружено
        # Создание объекта книги с параметрами из формы запроса и идентификатором изображения
        book = Book(**params(), cover_id=image_id)
        db.session.add(book)  # Добавление книги в сессию базы данных
        db.session.commit()  # Фиксация транзакции
    except IntegrityError as err:
        # Обработка ошибки целостности данных
        print(f'\n\n{err}\n\n')  # Вывод ошибки в консоль
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')  # Вывод сообщения об ошибке
        db.session.rollback()  # Откат транзакции
        # Повторное получение списка жанров из базы данных
        genres = list(item.name for item in db.session.execute(db.select(Genre)).scalars().all())
        # Рендеринг страницы добавления книги с переданным списком жанров
        return render_template('book_add.html', genres_list=genres)

    flash('Книга была успешно добавлена!', 'success')  # Вывод сообщения об успешном добавлении книги

    return redirect(url_for('index'))  # Перенаправление на главную страницу

# Маршрут для редактирования книги, поддерживающий методы GET и POST
@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    if request.method == 'POST':  # Обработка данных формы, если метод запроса POST
        book = Book.query.filter_by(id=book_id).first()  # Получение объекта книги по идентификатору

        # Обновление атрибутов книги параметрами из формы запроса
        for key, value in params().items():
            setattr(book, key, value)

        db.session.commit()  # Фиксация транзакции

        flash(f'Внесенные изменения были успешно добавлены!', 'success')  # Вывод сообщения об успешном обновлении
        return redirect(url_for('index'))  # Перенаправление на главную страницу

    book = Book.query.filter_by(id=book_id).first()  # Получение объекта книги по идентификатору

    genres = list()  # Список жанров

    # Получение списка всех жанров из базы данных и добавление их в список
    for item in db.session.execute(db.select(Genre)).scalars().all():
        genres.append(item.name)

    # Рендеринг страницы редактирования книги с переданными данными о книге и списком жанров
    return render_template('book_edit.html', book=book, genres_list=genres)
