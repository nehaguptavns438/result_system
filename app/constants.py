import os
class Email_data:
    EMAIL = os.environ.get('EMAIL')
    PASSWORD = os.environ.get('PASSWORD')
    
class Admin_data:
    USERNAME = os.environ.get('USERNAME')
    PASSWORD = os.environ.get('PASS')

class Setting:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('JAWSDB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 




