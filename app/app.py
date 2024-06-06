from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from auth import bp as auth_bp, init_login_manager
from models import db, User, Image, Book, Review, LinkTableBookGenre, Genre

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

@app.route('/')
def index():
    books_list = db.session.execute(db.select(Book)).scalars().all()

    genre_list = list()

    for book in books_list:
        reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()
        general_list = db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book.id).all()

        for item in general_list:
            genre_list = db.session.query(Genre).filter(Genre.id == item.genre_id).all()

    total_score = 0

    for review in reviews_list:
        total_score += review.mark

    user_obj = None

    if current_user.is_authenticated:
        user_obj = db.session.query(User).filter(User.login == current_user.login).first()
    
    return render_template(
        'index.html', 
        user_obj=user_obj, 
        books_list=books_list,
        genre_list=genre_list,
        average_score=total_score / len(reviews_list),
        number_of_reviews=len(reviews_list)
    )
    
@app.route('/images/<image_id>')
def image(image_id):
    img = db.get_or_404(Image, image_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)
