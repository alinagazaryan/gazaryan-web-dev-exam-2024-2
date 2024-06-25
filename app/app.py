from config import PER_PAGE
from book import bp as books_bp
from history import bp as history_bp
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from auth import bp as auth_bp, init_login_manager
from models import db, Image, Book, Review, LinkTableBookGenre, Genre
from flask import Flask, render_template, send_from_directory, request, session

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)

init_login_manager(app)

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(history_bp)


@app.route('/')
def index():
    # Очистка сохраненных данных ввода в сессии
    session['save_input_data'] = {}
    
    # Получение номера страницы из параметров запроса (по умолчанию 1)
    page = request.args.get('page', 1, type=int)
    
    # Создание запроса к базе данных для получения списка книг, отсортированных по году в порядке убывания
    books_list = Book.query.order_by(Book.year.desc())
    
    # Применение пагинации к запросу
    pagination = books_list.paginate(page=page, per_page=PER_PAGE)
    
    # Получение списка книг для текущей страницы
    books_list = pagination.items
    
    # Создание пустого списка для хранения данных о книгах
    data = list()

    # Обработка данных для каждой книги на текущей странице
    for book in books_list:
        # Получение всех отзывов для данной книги
        reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()
        
        # Получение всех жанров, связанных с данной книгой
        general_list = db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book.id).all()

        # Создание списка для хранения имен жанров
        genres = list()

        # Получение имен жанров и добавление их в список
        for item in general_list:
            genre_obj = db.session.query(Genre).filter(Genre.id == item.genre_id).first()
            genres.append(genre_obj.name)

        # Инициализация переменной для подсчета общего количества баллов от отзывов
        total_score = 0

        # Подсчет общего количества баллов от отзывов
        for review in reviews_list:
            total_score += review.mark

        # Вычисление среднего рейтинга книги
        try:
            average_mark = total_score / len(reviews_list)
        except ZeroDivisionError:
            average_mark = 0

        # Формирование словаря с информацией о книге и добавление его в список данных
        data.append({
            'book_id': book.id, 
            'book_name': book.name, 
            'genres': ', '.join(genres), 
            'book_year': book.year, 
            'average_score': average_mark,
            'number_of_reviews': len(reviews_list)
        })
    
    # Рендеринг шаблона index.html с переданными данными и объектом пагинации
    return render_template(
        'index.html', 
        data=data,
        pagination=pagination
    )

@app.route('/images/<image_id>')
def image(image_id):
    # Очистка сохраненных данных ввода в сессии
    session['save_input_data'] = {}
    
    # Получение изображения по ID или возврат ошибки 404, если изображение не найдено
    img = db.get_or_404(Image, image_id)
    
    # Отправка файла изображения из папки UPLOAD_FOLDER
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)

if __name__ == '__main__':
    app.run(port=8000)