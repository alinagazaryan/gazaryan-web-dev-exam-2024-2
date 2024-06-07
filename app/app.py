from books import bp as books_bp
from flask_migrate import Migrate
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from auth import bp as auth_bp, init_login_manager
from flask import Flask, render_template, send_from_directory
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
app.register_blueprint(books_bp)

@app.route('/')
def index():
    books_list = sorted(
        db.session.execute(db.select(Book)).scalars().all(), 
        key=lambda x: x.year, reverse=True
    )

    data = list()

    for book in books_list:
        reviews_list = db.session.query(Review).filter(Review.book_id == book.id).all()
        general_list = db.session.query(LinkTableBookGenre).filter(LinkTableBookGenre.book_id == book.id).all()

        genres = list()

        for item in general_list:
            genre_obj = db.session.query(Genre).filter(Genre.id == item.genre_id).first()
            genres.append(genre_obj.name)

        total_score = 0

        for review in reviews_list:
            total_score += review.mark

        try:
            average_mark = total_score / len(reviews_list)
        except ZeroDivisionError:
            average_mark = 0

        data.append({
            'book_id': book.id, 
            'book_name': book.name, 
            'genres': ', '.join(genres), 
            'book_year': book.year, 
            'average_score': average_mark,
            'number_of_reviews': len(reviews_list)
        })
    
    return render_template(
        'index.html', 
        data=data
    )
    
@app.route('/images/<image_id>')
def image(image_id):
    img = db.get_or_404(Image, image_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)

if __name__ == '__main__':
    app.run(port=8000)