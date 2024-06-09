from flask_login import current_user

class UsersPolicy:
    def __init__(self, record):
        self.record = record

    def show(self):
        return True

    def add(self):
        return current_user.is_admin
    
    def edit(self):
        return current_user.is_moder

    def remove(self):
        return current_user.is_admin

    # def show_log(self):
    #     return current_user.is_admin