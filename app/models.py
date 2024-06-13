import os, markdown
from flask import url_for
from datetime import datetime
from sqlalchemy import MetaData
from typing import Optional, List
from flask_login import UserMixin
from users_policy import UsersPolicy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import check_password_hash
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

RATING_WORDS={
    5: 'Отлично',
    4: 'Хорошо',
    3: 'Удовлетворительно',
    2: 'Неудовлетворительно',
    1: 'Плохо',
    0: 'Ужасно',
}

class Base(DeclarativeBase):
    metadata=MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db=SQLAlchemy(model_class=Base)

class Book(db.Model):
    __tablename__='books'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100), unique=True)
    short_desc: Mapped[str]=mapped_column(Text, nullable=False)
    year: Mapped[int]=mapped_column(String(10), nullable=False)
    publisher: Mapped[str]=mapped_column(String(100), nullable=False)
    author: Mapped[str]=mapped_column(String(100), nullable=False)
    volume: Mapped[int]=mapped_column(nullable=False)
    cover_id: Mapped[int]=mapped_column(ForeignKey('images.id'))

    review_of_book: Mapped[List['Review']]=relationship(back_populates='book', cascade='all, delete')
    history_of_book: Mapped[List['History']]=relationship(back_populates='book', cascade='all, delete')

    @property
    def markdown_desc(self):
        return markdown.markdown(self.short_desc)

class Genre(db.Model):
    __tablename__='genres'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100), unique=True, nullable=False)

class LinkTableBookGenre(db.Model):
    __tablename__='book_genres'
    id: Mapped[int]=mapped_column(primary_key=True)
    book_id: Mapped[int]=mapped_column(ForeignKey('books.id'))
    genre_id: Mapped[int]=mapped_column(ForeignKey('genres.id'))

class Image(db.Model):
    __tablename__='images'
    id: Mapped[str]=mapped_column(String(100), primary_key=True)
    file_name: Mapped[str]=mapped_column(String(100), nullable=False)
    mime_type: Mapped[str]=mapped_column(String(100), nullable=False)
    md5_hash: Mapped[str]=mapped_column(String(256), nullable=False, unique=True)

    @property
    def storage_filename(self):
        _, ext=os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('image', image_id=self.id)

class User(db.Model, UserMixin):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    first_name: Mapped[str]=mapped_column(String(100), nullable=False)
    last_name: Mapped[str]=mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]]=mapped_column(String(100), nullable=True)
    login: Mapped[str]=mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str]=mapped_column(String(256), nullable=False)

    role_id: Mapped[int]=mapped_column(ForeignKey('roles.id'))
    role: Mapped['Role']=relationship(back_populates='user_role')

    user_review: Mapped[List['Review']]=relationship(back_populates='user')
    user_actions_history: Mapped[List['History']]=relationship(back_populates='user')

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])
    
    @property
    def is_admin(self):
        return self.role.name == 'Администратор'

    @property
    def is_moder(self):
        return (self.role.name == 'Администратор' or self.role.name == 'Модератор')
    
    def can(self, action, record = None):
        users_policy = UsersPolicy(record)
        method = getattr(users_policy, action, None)
        return method() if method else False

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    __tablename__='roles'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100), nullable=False)
    desc: Mapped[str]=mapped_column(Text, nullable=False)

    user_role: Mapped['User'] = relationship(back_populates='role')

class Review(db.Model):
    __tablename__='reviews'
    id: Mapped[int]=mapped_column(primary_key=True)
    mark: Mapped[int]=mapped_column(nullable=False)
    text: Mapped[str]=mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]=mapped_column(default=datetime.now)

    book_id: Mapped[int]=mapped_column(ForeignKey('books.id'))
    book: Mapped['Book']=relationship(back_populates="review_of_book")

    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'))
    user: Mapped['User']=relationship(back_populates="user_review")

    @property
    def rating_word(self):
        return RATING_WORDS.get(self.mark)
    
    @property
    def markdown_review(self):
        return markdown.markdown(self.text)
    
class History(db.Model):
    __tablename__ = 'histories'
    id: Mapped[int]=mapped_column(primary_key=True)
    created_at: Mapped[datetime]=mapped_column(default=datetime.now)

    book_id: Mapped[int]=mapped_column(ForeignKey('books.id'))
    book: Mapped['Book']=relationship(back_populates="history_of_book")
    
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'))
    user: Mapped['User']=relationship(back_populates="user_actions_history")