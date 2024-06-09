import functools
from models import db, User
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    return user

def permission_check(action):
    def decor(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            user = None
            if user_id:
                user = load_user(user_id)
            if not current_user.can(action, user):
                flash('У вас недостаточно прав для выполнения данного действия', 'warning')
                return redirect(url_for('index'))
            return function(*args, **kwargs)
        return wrapper
    return decor

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        check_remember = True if request.form.get('remember_me') else False 
        if login and password:
            user = db.session.execute(db.select(User).filter_by(login=login)).scalar()
            if user and user.check_password(password):
                login_user(user, remember=check_remember)
                flash('Вы успешно аутентифицированы.', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('index'))
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
