# / Some of code has been copied from Corey Shaffer's flask application
# https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin




app = Flask(__name__)
app.config['SECRET_KEY'] = '9b5d1b2a5a02c837aecabf4849310efa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='Admin',template_mode='bootstrap3')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manger = LoginManager(app)
login_manger.login_view = 'login'
login_manger.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bbworkatfhsu@gmail.com'
app.config['MAIL_PASSWORD'] = 'Blackboard@Fhsu!'
mail = Mail(app)


from flaskbb import routes