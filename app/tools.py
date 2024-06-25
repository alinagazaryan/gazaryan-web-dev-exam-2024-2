# Импорт необходимых модулей и функций
import uuid, os, hashlib 
from models import db, Image
from flask import current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from config import UPLOAD_FOLDER

# Класс для сохранения изображений
class ImageSaver:
    # Инициализация с файлом, который нужно сохранить
    def __init__(self, file):
        self.file = file

    # Метод для создания данных о файле изображения
    def create_file_data(self):
        # Проверка на наличие изображения в базе данных по его MD5-хэшу
        self.img = self.__find_by_md5_hash()
        # Если изображение уже существует, возвращаем его
        if self.img is not None:
            return self.img
        # Безопасное получение имени файла
        file_name = secure_filename(self.file.filename)
        # Создание новой записи об изображении в базе данных
        self.img = Image(
            id=str(uuid.uuid4()),  # Генерация уникального идентификатора для изображения
            file_name=file_name,  # Имя файла
            mime_type=self.file.mimetype,  # MIME-тип файла
            md5_hash=self.md5_hash)  # MD5-хэш файла
        # Установка имени файла хранения
        self.img.file_name = self.img.storage_filename
        return self.img
    
    # Метод для сохранения файла изображения на диск
    def download(self, img):
        try:
            # Сохранение файла по указанному пути
            self.file.save(
                os.path.join(current_app.config['UPLOAD_FOLDER'],
                            img.storage_filename))
            # Добавление записи об изображении в базу данных
            db.session.add(img)
            # Подтверждение транзакции
            db.session.commit()
        except SQLAlchemyError:
            # Откат транзакции в случае ошибки
            db.session.rollback()
            return None
        return True

    # Приватный метод для поиска изображения по его MD5-хэшу
    def __find_by_md5_hash(self):
        # Вычисление MD5-хэша файла
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        # Возврат курсора файла на начало
        self.file.seek(0)
        # Поиск изображения в базе данных по MD5-хэшу
        return db.session.execute(db.select(Image).filter(Image.md5_hash == self.md5_hash)).scalar()

# Класс для удаления изображений
class ImageDeleter:
    # Инициализация с объектом изображения, которое нужно удалить
    def __init__(self, img):
        self.img = img

    # Метод для удаления изображения
    def delete(self, books_used_cover):
        try:
            # Если данное изображение используется только одной книгой, удаляем его
            if books_used_cover == 1:
                # Удаление файла изображения с диска
                os.remove(os.path.join(UPLOAD_FOLDER, self.img.storage_filename))
                # Удаление записи об изображении из базы данных
                db.session.delete(self.img)
                # Подтверждение транзакции
                db.session.commit()
        except SQLAlchemyError:
            # Откат транзакции в случае ошибки
            db.session.rollback()
