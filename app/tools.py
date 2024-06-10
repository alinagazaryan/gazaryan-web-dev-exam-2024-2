import uuid, os, hashlib 
from models import db, Image
from flask import current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from config import UPLOAD_FOLDER

class ImageSaver:
    def __init__(self, file):
        self.file = file

    def create_file_data(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.img
        file_name = secure_filename(self.file.filename)
        self.img = Image(
            id=str(uuid.uuid4()),
            file_name=file_name,
            mime_type=self.file.mimetype,
            md5_hash=self.md5_hash)
        return self.img
    
    def download(self, img):
        try:
            self.file.save(
                os.path.join(current_app.config['UPLOAD_FOLDER'],
                            img.storage_filename))
            db.session.add(img)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return None
        return True

    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Image).filter(Image.md5_hash == self.md5_hash)).scalar()

class ImageDeleter:
    def __init__(self, img):
        self.img = img

    def delete(self):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, self.img.storage_filename))
            db.session.delete(self.img)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()