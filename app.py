from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, UserMixin, RoleMixin
from datetime import datetime
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
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
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_REGISTER_USER_TEMPLATE'] = 'register.html'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/courses'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/my_courses'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['SECURITY_URL_PREFIX'] = '/'

babel = Babel(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                       )


courses_users = db.Table('courses_users',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
                         )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    courses = db.relationship('Course', secondary=courses_users, backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return f'Профиль {self.email}'

    def __repr__(self):
        return self.email


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Общая')
    short_description = db.Column(db.Text, nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=True)  # Описание курса
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.id


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)



admin = Admin(app)

class UserAdmin(ModelView):
    column_searchable_list = ['email']
    column_filters = ['confirmed_at', 'active']

    can_edit = False
    can_create = False


class CourseAdmin(ModelView):
    column_searchable_list = ['title', 'author']
    column_filters = ['author', 'category']


admin.add_view(UserAdmin(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(CourseAdmin(Course, db.session))

@app.route('/admin', endpoint='admin')
@login_required
def admin():
    if any(role.name == 'админ' for role in current_user.roles):
        return render_template('admin/index.html')
    return render_template('no_access.html')


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


@app.route('/my_courses', endpoint='user_courses')
@login_required
def user_courses():
    courses = current_user.courses
    return render_template('user_courses.html', courses=courses)


@app.route('/courses', endpoint='all_courses')
def all_courses():
    courses = Course.query.all()
    return render_template('all_courses.html', courses=courses)


@app.route('/about_course_<int:course_id>', endpoint='about_course')
def about_course(course_id):
    course = Course.query.get(course_id)

    return render_template('about_course.html', course=course)


@app.route('/courses/course_<int:course_id>', endpoint='course_page')
@login_required
def course_page(course_id):
    course = Course.query.get(course_id)

    return render_template('course_page.html', course=course)


@app.route('/start_course_<int:course_id>', endpoint='start_course')
@login_required
def start_course(course_id):
    course = Course.query.get(course_id)

    if course not in current_user.courses:
        current_user.courses.append(course)
        db.session.commit()

        return redirect(url_for('course_page', course_id=course.id))

    return render_template('course_page.html', course=course)
