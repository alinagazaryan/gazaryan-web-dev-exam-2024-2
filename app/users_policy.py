from flask_login import current_user

# Класс UsersPolicy для определения политик доступа пользователей
class UsersPolicy:
    # Инициализация объекта класса с записью, к которой применяется политика
    def __init__(self, record):
        self.record = record

    # Метод для проверки права на просмотр записи, всегда возвращает True
    def show(self):
        return True

    # Метод для проверки права на добавление записи
    def add(self):
        # Разрешение на добавление записи есть только у администратора
        return current_user.is_admin
    
    # Метод для проверки права на редактирование записи
    def edit(self):
        # Разрешение на редактирование записи есть только у модератора
        return current_user.is_moder

    # Метод для проверки права на удаление записи
    def remove(self):
        # Разрешение на удаление записи есть только у администратора
        return current_user.is_admin

    # Метод для проверки права на просмотр логов
    def check_logs(self):
        # Разрешение на просмотр логов есть только у администратора
        return current_user.is_admin
