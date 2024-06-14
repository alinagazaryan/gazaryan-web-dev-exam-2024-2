import os

SECRET_KEY = 'c21b53cf1799629b3ac0acd3a46581c5afd4b370127f7d2ee3face937142'

# SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\Users\\Huawei\\Desktop\\app\\database.sqlite3'
SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\Users\\Huawei\\Desktop\\web_ex\\gazaryan-web-dev-exam-2024-2\\app\\database.sqlite3'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

PER_PAGE = 10

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')