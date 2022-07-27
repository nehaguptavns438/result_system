import os
class Email_data:
    EMAIL = os.environ.get('EMAIL')
    PASSWORD = os.environ.get('PASSWORD')
    
class Admin_data:
    USERNAME = os.environ.get('USERNAME')
    PASSWORD = os.environ.get('PASS')

class Setting:
    # SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('JAWSDB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    # WKHTMLTOPDF_DOWNLOAD_URL = "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb"





