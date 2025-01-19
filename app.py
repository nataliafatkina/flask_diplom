from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, UserMixin, RoleMixin
from flask_security.utils import hash_password
from flask_babel import Babel
import uuid

app = Flask(__name__)

app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['SECRET_KEY'] = 'scfedo786@DS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///course_site.db'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'Sxcv8632nbhk'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_EMAIL_VALIDATOR_ARGS'] = {'check_deliverability': False}
app.config['SECURITY_PASSWORD_COMPLEXITY'] = True
# app.config['SECURITY_USERNAME_MIN_LENGTH'] = 3
# app.config['SECURITY_USERNAME_MAX_LENGTH'] = 20
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'register.html'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/my_courses'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['SECURITY_URL_PREFIX'] = '/'

babel = Babel(app)

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                       )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/home', endpoint='home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("Email:", request.form.get('email'))
        print("Password:", request.form.get('password'))
        print("Password Confirm:", request.form.get('password_confirm'))
    return render_template('register.html')


@app.route('/')
def main():
    return redirect(url_for('home'))


@app.route('/logout', endpoint='logout')
def logout():
    return redirect(url_for('home'))


@app.route('/profile', endpoint='profile')
@login_required
def profile():
    return render_template('profile.html')



@app.route('/my_courses')
@login_required
def user_courses():
    return render_template('user_courses.html')


with app.app_context():
    print(app.url_map)
