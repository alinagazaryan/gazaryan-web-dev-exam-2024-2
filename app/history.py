import datetime, io
from models import db
from config import PER_PAGE
from models import History, Book
from sqlalchemy import func, desc
from auth import permission_check
from flask_login import login_required
from flask import Blueprint, render_template, request, send_file, session

bp = Blueprint('history', __name__, url_prefix='/history')

# Функция для создания CSV файла из данных и списка полей
def make_file(data, fields):
    # Создание строки заголовка CSV файла с номерами и полями
    csv_content = '№,' + ','.join(fields) + '\n'
    # Перебор данных и создание строк для каждого элемента
    for i, item in enumerate(data):
        # Извлечение значений для указанных полей
        values = [str(item.get(f, '')) for f in fields]
        # Добавление строки с номером и значениями в CSV контент
        csv_content += f'{i+1},' + ','.join(values) + '\n'
    # Создание байтового потока для записи CSV данных
    f = io.BytesIO()
    # Запись закодированного в utf-8 содержимого CSV файла в байтовый поток
    f.write(csv_content.encode('utf-8'))
    # Перемещение указателя потока в начало
    f.seek(0)
    # Возвращение байтового потока
    return f

# Маршрут для отображения активности пользователей, доступен только авторизованным пользователям с соответствующим разрешением
@bp.route('/users_activity')
@login_required
@permission_check('check_logs')
def users_activity():
    # Сброс сохраненных данных формы в сессии
    session['save_input_data'] = {}
    # Получение всех записей истории, отсортированных по дате создания в порядке убывания
    all_records = History.query.order_by(History.created_at.desc())
    records = all_records  # Инициализация переменной для текущей страницы записей
    # Получение текущей страницы из параметров запроса, по умолчанию 1
    page = request.args.get('page', 1, type=int)

    # Пагинация записей с указанной страницей и количеством записей на странице
    pagination = records.paginate(page=page, per_page=PER_PAGE)
    records = pagination.items  # Записи для текущей страницы

    data = list()  # Список для хранения данных текущей страницы
    all_data = list()  # Список для хранения всех данных

    # Перебор всех записей истории
    for record in all_records:
        # Добавление данных о книге и времени создания записи
        all_data.append({
            'author': record.book.author,
            'name': record.book.name,
            'created_at': record.created_at
        })
        # Добавление данных о пользователе
        if record.user == None:
            all_data[len(all_data) - 1]['full_name'] = 'Неаутентифицированный пользователь'
        else:
            all_data[len(all_data) - 1]['full_name'] = record.user.full_name

    # Перебор записей текущей страницы
    for record in records:
        # Добавление данных о книге и времени создания записи
        data.append({
            'author': record.book.author,
            'name': record.book.name,
            'created_at': record.created_at
        })
        # Добавление данных о пользователе
        if record.user == None:
            data[len(data) - 1]['full_name'] = 'Неаутентифицированный пользователь'
        else:
            data[len(data) - 1]['full_name'] = record.user.full_name

    # Если параметр запроса содержит 'download_csv_file', создается и отправляется CSV файл
    if request.args.get('download_csv_file'):
        f = make_file(all_data, ['full_name', 'author', 'name', 'created_at'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='users_activity.csv')

    # Рендеринг страницы активности пользователей с данными и пагинацией
    return render_template(
        'history/users_activity.html',
        pagination=pagination,
        data=data
    )

# Маршрут для отображения статистики книг, доступен только авторизованным пользователям с соответствующим разрешением
@bp.route('/books_statistic', methods=['GET', 'POST'])
@login_required
@permission_check('check_logs')
def books_statistic():
    # Сброс сохраненных данных формы в сессии
    session['save_input_data'] = {}
    # Получение текущей страницы из параметров запроса, по умолчанию 1
    page = request.args.get('page', 1, type=int)

    # Получение всех записей истории с количеством обращений к каждой книге
    all_records = History.query.with_entities(History.book_id, 
        func.count(History.book_id).label('count')).filter(
        History.user_id.isnot(-1)).group_by(
        History.book_id).order_by(desc('count'))
    
    records = all_records  # Инициализация переменной для текущей страницы записей

    # Если метод запроса POST, фильтрация по дате
    if request.method == 'POST':
        date_from = request.form['date-from']  # Получение начальной даты из формы
        date_to = request.form['date-to']  # Получение конечной даты из формы

        # Фильтрация записей по начальной дате, если она указана
        if date_from:
            records = records.filter(History.created_at >= date_from)

        # Фильтрация записей по конечной дате, если она указана
        if date_to:
            date_to_next_day = datetime.datetime.strptime(date_to, "%Y-%m-%d") + datetime.timedelta(days=1)
            records = records.filter(History.created_at <= date_to_next_day)

    # Пагинация записей с указанной страницей и количеством записей на странице
    pagination = records.paginate(page=page, per_page=PER_PAGE)
    records = pagination.items  # Записи для текущей страницы

    data = list()  # Список для хранения данных текущей страницы

    # Перебор записей текущей страницы
    for book_id, count in records:
        book = db.session.query(Book).filter(Book.id == book_id).first()  # Получение объекта книги по идентификатору
        data.append({
            'author': book.author,
            'name': book.name,
            'count': count  # Добавление данных о книге и количестве обращений
        })

    all_data = list()  # Список для хранения всех данных

    # Перебор всех записей
    for book_id, count in all_records:
        book = db.session.query(Book).filter(Book.id == book_id).first()  # Получение объекта книги по идентификатору
        all_data.append({
            'author': book.author,
            'name': book.name,
            'count': count  # Добавление данных о книге и количестве обращений
        })

    # Если параметр запроса содержит 'download_csv_file', создается и отправляется CSV файл
    if request.args.get('download_csv_file'):
        f = make_file(all_data, ['author', 'name', 'count'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='books_statistic.csv')

    # Рендеринг страницы статистики книг с данными и пагинацией
    return render_template(
        'history/books_statistic.html',
        pagination=pagination,
        data=data
    )
