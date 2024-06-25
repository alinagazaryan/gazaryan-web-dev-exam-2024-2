import bleach, datetime
from sqlalchemy import func
from auth import permission_check
from flask_login import current_user
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from tools import ImageSaver, ImageDeleter
from models import db, Book, Genre, LinkTableBookGenre, Review, Image, History
from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response, session

bp = Blueprint('book', __name__, url_prefix='/book')

BOOKS_PARAMS = [
    'name', 'short_desc', 'year', 'author', 'publisher', 'volume'
]

# Функция для получения параметров из формы запроса
def params():
    return { p: request.form.get(p) or None for p in BOOKS_PARAMS }

# Функция для вставки данных в таблицу связей книг и жанров
def insert_data_into_table_book_genres(book, choice_genres):
    # Удаление всех текущих связей книги с жанрами
    db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book.id).delete()

    # Добавление новых связей книги с жанрами
    for genre_id in choice_genres:
        book_genre = LinkTableBookGenre(book_id=book.id, genre_id=genre_id)
        db.session.add(book_genre)  # Добавление новой записи в сессию

# Маршрут для отображения популярных книг
@bp.route('/popular')
def popular_books():
    # Очистка сохраненных данных ввода в сессии
    session['save_input_data'] = {}
    
    # Получение даты трех месяцев назад от текущей даты
    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=3 * 30)

    # Запрос к базе данных для получения книг, упоминавшихся в истории за последние три месяца
    records = History.query.with_entities(History.book_id).filter(
        History.created_at >= three_months_ago).group_by(
        History.book_id).order_by(func.count(History.book_id).desc()).limit(5).all()
    
    # Создание списка для хранения данных о популярных книгах
    data = list()
    
    # Обработка данных для каждой книги из запроса
    for record in sum(list(map(list, records)), list()):
        book = db.session.query(Book).filter(Book.id == record).first()
        reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()

        # Вычисление среднего рейтинга книги
        try:
            average_score = sum(review.mark for review in reviews_list) / len(reviews_list)
        except ZeroDivisionError:
            average_score = 0

        # Формирование словаря с информацией о книге и добавление его в список данных
        data.append({
            'book_id': book.id,
            'cover': book.cover_id,
            'name': book.name,
            'author': book.author,
            'average_score': average_score
        })

    # Рендеринг шаблона popular_books.html с переданными данными
    return render_template('popular_books.html', data=data)

# Маршрут для отображения недавно просмотренных книг
@bp.route('/recently')
def recently_books():
    # Очистка сохраненных данных ввода в сессии
    session['save_input_data'] = {}
    
    # Создание списка для хранения средних оценок книг
    average_score_list = list()

    # Попытка получить недавно просмотренные книги для текущего пользователя или анонимного пользователя
    try:
        recently_books = request.cookies.get(f'recently_books_{current_user.id}')
    except AttributeError:
        recently_books = request.cookies.get('recently_books_anonymous')

    # Если недавно просмотренные книги найдены
    if recently_books:
        # Преобразование строковых идентификаторов книг в объекты книг
        recently_books = list(map(Book.query.get, recently_books.split(',')))

        # Вычисление среднего рейтинга для каждой книги
        for book in recently_books:
            reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()
            try:
                average_score_list.append(sum(review.mark for review in reviews_list) / len(reviews_list))
            except ZeroDivisionError:
                average_score_list.append(0)

    # Рендеринг шаблона recently_books.html с переданными данными
    return render_template(
        'recently_books.html',
        history=recently_books,
        average_score_list=average_score_list
    )
    
    
# Маршрут для отображения формы добавления новой книги
@bp.route('/new')
@login_required  # Требует аутентификации пользователя
@permission_check('add')  # Проверяет наличие прав на добавление
def new():
    # Получение списка жанров из базы данных
    genres = list(item for item in db.session.execute(db.select(Genre)).scalars().all())
    # Рендеринг страницы добавления книги с переданным списком жанров
    return render_template('book_add.html', genres_list=genres)

# Маршрут для обработки данных формы добавления новой книги
@bp.route('/add', methods=['POST'])
@login_required  # Требует аутентификации пользователя
@permission_check('add')  # Проверяет наличие прав на добавление
def add():
    # Получение списка жанров из базы данных
    genres = list(item for item in db.session.execute(db.select(Genre)).scalars().all())
    f = request.files.get('background_img')  # Получение файла изображения обложки из формы
    img = None

    # Сохранение данных формы в сессии
    session['save_input_data'] = params()

    # Проверка на заполнение всех обязательных полей формы
    if any(value is None for value in params().values()):
        flash('Заполните все поля', 'warning')
        return render_template('book_add.html', genres_list=genres)

    # Проверка на числовое значение поля "Год издания"
    if not params().get('year').isdigit():
        flash('Поле "Год издания" должно быть числом', 'warning')
        return render_template('book_add.html', genres_list=genres)

    # Проверка на числовое значение поля "Объем книги"
    if not params().get('volume').isdigit():
        flash('Поле "Объем книги" должно быть числом', 'warning')
        return render_template('book_add.html', genres_list=genres)

    # Проверка на наличие файла изображения
    if f and f.filename:
        img = ImageSaver(f).create_file_data()  # Создание данных файла изображения
    else:
        flash('Загрузите обложку для книги', 'warning')
        return render_template('book_add.html', genres_list=genres)

    # Получение списка жанров из формы
    genres_from_form = request.form.getlist('genres_filter')

    # Проверка на выбор жанра
    if genres_from_form[0] == 'default':
        flash('Выберите жанр(ы) для книги', 'warning')
        return render_template('book_add.html', genres_list=genres)
    else:
        choice_genres = list(map(int, request.form.getlist('genres_filter')))  # Преобразование списка жанров в числа

    # Создание объекта книги с параметрами из формы и ID обложки
    book = Book(**params(), cover_id=img.id)
    book.short_desc = bleach.clean(book.short_desc)  # Очистка краткого описания книги

    try:
        db.session.add(book)  # Добавление объекта книги в сессию

        insert_data_into_table_book_genres(book, choice_genres)  # Вставка данных в таблицу связей книг и жанров

        db.session.commit()  # Фиксация транзакции

        # Попытка загрузки изображения
        if ImageSaver(f).download(img):
            flash('Книга была успешно добавлена!', 'success')
            session['save_input_data'] = {}
            return redirect(url_for('book.show', book_id=book.id))  # Перенаправление на страницу книги
        else:
            flash('Возникла ошибка при загрузке обложки', 'danger')
            return render_template('book_add.html', genres_list=genres)
        
    except IntegrityError:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        db.session.rollback()  # Откат транзакции при ошибке
        return render_template('book_add.html', genres_list=genres)
    
    
  
# Маршрут для отображения и обработки данных страницы книги
@bp.route('/<int:book_id>/show', methods=['GET', 'POST'])
def show(book_id):
    session['save_input_data'] = {}  # Очистка данных сессии, используемых для сохранения введенных данных

    # Исключение для обработки случая, когда пользователь является анонимным
    try:
        count = History.query.filter(History.user_id == current_user.id, History.book_id == book_id, 
            func.date(History.created_at) == datetime.date.today()).count()
    except AttributeError:
        count = History.query.filter(History.user_id == -1, History.book_id == book_id, 
            func.date(History.created_at) == datetime.date.today()).count()

    # Если пользователь просматривал книгу менее 10 раз за день, добавляем запись в историю
    if count < 10:
        try:
            db.session.add(History(book_id=book_id, user_id=current_user.id))
        except AttributeError:
            db.session.add(History(book_id=book_id, user_id=-1))
        db.session.commit()  # Фиксация транзакции

    # Получение объекта книги по идентификатору
    book = db.session.query(Book).filter(Book.id == book_id).first()

    # Получение списка отзывов для книги
    reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()

    # Проверка возможности написания отзыва текущим пользователем
    try:
        can_write_review = not bool(Review.query.filter_by(user_id=current_user.id).filter_by(book_id=book_id).first())
    except AttributeError:
        can_write_review = False

    # Расчет среднего рейтинга книги
    try:
        average_score = sum(review.mark for review in reviews_list) / len(reviews_list)
    except ZeroDivisionError:
        average_score = 0

    # Получение списка недавно просмотренных книг из cookies
    try:
        recently_books = request.cookies.get(f'recently_books_{current_user.id}')
    except AttributeError:
        recently_books = request.cookies.get('recently_books_anonymous')

    recently_books = recently_books.split(',') if recently_books else list()  # Преобразование строки в список

    # Обновление списка недавно просмотренных книг
    if str(book_id) in recently_books:
        recently_books.remove(str(book_id))
        recently_books.insert(0, str(book_id))
    else:
        recently_books.insert(0, str(book_id))

    recently_books_str = ','.join(recently_books[:5])  # Преобразование списка в строку

    # Создание ответа с рендерингом шаблона show.html и переданными данными
    response = make_response(render_template(
        'show.html', 
        book=book, 
        reviews_list=reviews_list,
        average_score=average_score,
        number_of_reviews=len(reviews_list),
        can_write_review=can_write_review
    ))

    # Установка cookies для недавно просмотренных книг
    try:
        response.set_cookie(f'recently_books_{current_user.id}', recently_books_str)
    except AttributeError:
        response.set_cookie('recently_books_anonymous', recently_books_str)

    return response  # Возврат ответа

# Маршрут для редактирования информации о книге
@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required  # Требует аутентификации пользователя
@permission_check('edit')  # Проверяет наличие прав на редактирование
def edit(book_id):
    session['save_input_data'] = {}  # Очистка данных сессии, используемых для сохранения введенных данных
    book = Book.query.filter_by(id=book_id).first()  # Получение объекта книги по идентификатору

    # Получение списка всех жанров из базы данных
    genres = list(item for item in db.session.execute(db.select(Genre)).scalars().all())

    # Получение списка жанров для текущей книги
    choice_genres = [item.genre_id for item in db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book_id).all()]

    # Обработка данных формы, если метод запроса POST
    if request.method == 'POST':
        book = Book.query.filter_by(id=book_id).first()  # Получение объекта книги по идентификатору

        # Проверка на заполнение всех обязательных полей формы
        if any(value is None for value in params().values()):
            flash('Поля не должны быть пустыми', 'warning')
            return render_template('book_edit.html', genres_list=genres, book=book)
        
        # Проверка на числовое значение поля "Год издания"
        if not params().get('year').isdigit():
            flash('Поле "Год издания" должно быть числом', 'warning')
            return render_template('book_edit.html', genres_list=genres, book=book)

        # Проверка на числовое значение поля "Объем книги"
        if not params().get('volume').isdigit():
            flash('Поле "Объем книги" должно быть числом', 'warning')
            return render_template('book_edit.html', genres_list=genres, book=book)
        
        # Получение списка жанров из формы
        genres_from_form = request.form.getlist('genres_filter')
    
        # Проверка на выбор жанра
        if genres_from_form[0] == 'default':
            flash('Выберите жанр(ы) для книги', 'warning')
            return render_template('book_edit.html', genres_list=genres, book=book)
        else:
            choice_genres = list(map(int, request.form.getlist('genres_filter')))  # Преобразование списка жанров в числа

        try:
            insert_data_into_table_book_genres(book, choice_genres)  # Вставка данных в таблицу связей книг и жанров
            db.session.commit()  # Фиксация транзакции
        except IntegrityError:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            db.session.rollback()  # Откат транзакции при ошибке
            return render_template('book_edit.html', genres_list=genres, book=book)

        # Обновление полей объекта книги значениями из формы
        for key, value in params().items():
            if key == 'short_desc' and value is not None:
                setattr(book, key, bleach.clean(value))  # Очистка краткого описания книги
            elif value is not None:
                setattr(book, key, value)

        db.session.commit()  # Фиксация транзакции

        flash('Внесенные изменения были успешно добавлены!', 'success')
        return redirect(url_for('index'))  # Перенаправление на главную страницу

    # Рендеринг страницы редактирования книги с переданными данными
    return render_template(
        'book_edit.html', 
        book=book, 
        genres_list=genres, 
        choice_genres=choice_genres
    )

    
    
# Маршрут для удаления книги
@bp.route('/<int:book_id>/remove', methods=['POST'])  # Определение маршрута, который принимает POST-запрос для удаления книги
@login_required  # Требует аутентификации пользователя
@permission_check('remove')  # Проверяет наличие прав на удаление
def remove(book_id):
    session['save_input_data'] = {}  # Очистка данных сессии, используемых для сохранения введенных данных
    
    # Получение объекта книги по идентификатору
    book = db.session.query(Book).filter(Book.id == book_id).first()

    # Получение всех жанров, связанных с книгой
    book_genres = db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book_id).all()

    # Получение объекта изображения по идентификатору обложки книги
    image = db.session.query(Image).filter(Image.id == book.cover_id).first()

    # Подсчет количества книг, использующих данное изображение
    books_used_cover = len(db.session.query(Book).filter(Book.cover_id == image.id).all())

    # Создание экземпляра класса для удаления изображения
    image_deleter = ImageDeleter(image)

    try:
        db.session.delete(book)  # Удаление книги из базы данных
        image_deleter.delete(books_used_cover)  # Удаление изображения, если оно больше не используется

        # Удаление всех связей книги с жанрами
        for item in book_genres:
            db.session.delete(item)
            
        db.session.commit()  # Фиксация транзакции
    except IntegrityError:
        flash('Не удалось выполнить удаление книги', 'danger')  # Вывод сообщения об ошибке
        db.session.rollback()  # Откат транзакции
        return redirect(url_for('index'))  # Перенаправление на главную страницу

    return redirect(url_for('index'))  # Перенаправление на главную страницу при успешном удалении

# Маршрут для добавления отзыва на книгу
@bp.route('/<int:book_id>/review_add', methods=['GET', 'POST'])  # Определение маршрута для добавления отзыва, поддерживающего GET и POST запросы
@login_required  # Требует аутентификации пользователя
def review_add(book_id):
    if request.method == 'POST':  # Обработка данных формы, если метод запроса POST
        # Проверка, оставлял ли текущий пользователь уже отзыв на эту книгу
        if Review.query.filter_by(user_id=current_user.id).filter_by(book_id=book_id).first():
            flash('Вы уже оставляли рецензию на эту книгу.', 'warning')  # Вывод предупреждения
            return redirect(url_for('book.show', book_id=book_id))  # Перенаправление на страницу книги

        text = bleach.clean(request.form['text'])  # Очистка текста отзыва от потенциально вредоносного HTML
        mark = request.form['mark']  # Получение оценки из формы
        
        try:
            # Добавление нового отзыва в базу данных
            db.session.add(
                Review(mark=mark, text=text, book_id=book_id, user_id=current_user.id)
            )
            db.session.commit()  # Фиксация транзакции
            return redirect(url_for('book.show', book_id=book_id))  # Перенаправление на страницу книги при успешном добавлении
        except IntegrityError:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')  # Вывод сообщения об ошибке
            db.session.rollback()  # Откат транзакции
            return render_template('review_add.html', book_id=book_id)  # Рендеринг страницы добавления отзыва

    book = db.session.query(Book).filter(Book.id == book_id).first()  # Получение объекта книги по идентификатору

    return render_template('review_add.html', book=book)  # Рендеринг страницы добавления отзыва с переданными данными о книге
