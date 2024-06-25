import functools
from models import db, User
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Инициализация LoginManager для приложения Flask
def init_login_manager(app):
    login_manager = LoginManager()  # Создание экземпляра LoginManager
    login_manager.login_view = 'auth.login'  # Указание представления для страницы входа
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'  # Сообщение, отображаемое при попытке доступа без аутентификации
    login_manager.login_message_category = 'warning'  # Категория сообщения для всплывающих уведомлений
    login_manager.user_loader(load_user)  # Указание функции загрузки пользователя
    login_manager.init_app(app)  # Инициализация LoginManager с приложением Flask

# Функция загрузки пользователя по его ID
def load_user(user_id):
    # Запрос к базе данных для получения пользователя по ID
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    return user  # Возврат объекта пользователя

# Декоратор для проверки прав доступа пользователя к определенному действию
def permission_check(action):
    def decor(function):
        @functools.wraps(function)  # Сохранение метаданных оригинальной функции
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')  # Получение ID пользователя из аргументов функции
            user = None
            if user_id:
                user = load_user(user_id)  # Загрузка пользователя по ID
            if not current_user.can(action, user):  # Проверка прав доступа текущего пользователя
                flash('У вас недостаточно прав для выполнения данного действия', 'warning')  # Вывод сообщения об ошибке
                return redirect(url_for('index'))  # Перенаправление на главную страницу
            return function(*args, **kwargs)  # Выполнение оригинальной функции
        return wrapper
    return decor

# Маршрут для страницы входа
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')  # Получение логина из формы
        password = request.form.get('password')  # Получение пароля из формы
        check_remember = True if request.form.get('remember_me') else False  # Проверка отметки "запомнить меня"
        if login and password:
            # Запрос к базе данных для получения пользователя по логину
            user = db.session.execute(db.select(User).filter_by(login=login)).scalar()
            if user and user.check_password(password):  # Проверка пароля пользователя
                login_user(user, remember=check_remember)  # Выполнение входа пользователя
                flash('Вы успешно аутентифицированы.', 'success')  # Вывод сообщения об успешной аутентификации
                next = request.args.get('next')  # Получение URL для перенаправления после входа
                return redirect(next or url_for('index'))  # Перенаправление на указанный URL или на главную страницу
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')  # Вывод сообщения об ошибке аутентификации
    return render_template('auth/login.html')  # Рендеринг страницы входа

# Маршрут для выхода пользователя
@bp.route('/logout')
@login_required  # Требуется аутентификация для доступа к маршруту
def logout():
    logout_user()  # Выполнение выхода пользователя
    return redirect(url_for('index'))  # Перенаправление на главную страницу

