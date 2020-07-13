# / Some of code has been copied from Corey Shaffer's flask application
# https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
from flaskbb import db, login_manger, app,admin,bcrypt
from flask import redirect,url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin,current_user
from flask_admin.contrib.sqla import ModelView

@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post',backref='author', lazy=True)

    def get_reset_token(self,expeire_sec=600):
        s = Serializer(app.config['SECRET_KEY'],expeire_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f" Post('{self.title}','{self.content}','{self.date_posted}')"

class AdminView(ModelView):
    def is_accessible(self):
        # return current_user.is_authenticated
        return current_user.username == 'm_tao'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin.add_view(AdminView(User,db.session))
admin.add_view(AdminView(Post,db.session))