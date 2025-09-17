from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import hashlib  # Для хэширования паролей
from functools import wraps
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '1h34b45h2j12ngg33j2'

# Инициализация Flask-Migrate
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    '''Функция для пост и гет запросов она принимает'''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return 'Пользователь с таким email уже существует'

        new_user = User(email=email)
        new_user.set_password(password)  # **Хэшируем пароль**
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/index')
        except:
            return 'При регистрации произошла ошибка'
    else:
        return render_template('sign_in.html')

@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

@app.route('/sign_up', methods=['POST','GET'])
def sign_up():
    '''Функция для входа пользователя'''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            return redirect('/index')  # Используйте url_for
        else:
            return 'Неверный логин или пароль'
    else:
        return render_template('login.html')
