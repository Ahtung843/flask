from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib  # Для хэширования паролей
from functools import wraps
from flask_migrate import Migrate
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = '1h34b45h2j12ngg33j2'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Время жизни сессии


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

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

# Декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('sign_up', next=request.url)) # Перенаправление на вход
        return f(*args, **kwargs)
    return decorated_function

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get('logged_in'), email=session.get('email'))

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

            # Автоматически войти после регистрации
            user = User.query.filter_by(email=email).first()
            session['logged_in'] = True
            session['user_id'] = user.id
            session['email'] = email
            session.permanent = True  # Сделать сессию постоянной

            return redirect('/index')
        except:
            return 'При регистрации произошла ошибка'
    else:
        return render_template('sign_in.html')


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
            session['email'] = email
            session.permanent = True  # Сохраняем сессию на 7 дней
            return redirect('/cabinet')
        else:
            return 'Неверный логин или пароль'
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/cabinet', methods=['POST','GET'])
def cabinet():
    '''Условие на проверку емаила в сессии(нужно для отображения емаила)'''
    if 'email' in session:
        print(f"Email в сессии: {session['email']}")  # <--- Добавьте эту строку для отладки

        if request.method == 'POST':
            name = request.form['name']
            price = request.form['price']
            text = request.form['description']

            try:
                # Преобразование price в float (или другой числовой тип)
                price = float(price)
                new_product = Product(name=name, price=price, text=text)
                db.session.add(new_product)
                db.session.commit()
                return redirect('/index')
            except ValueError as e:
                # Обработка ошибки преобразования price
                return f'Ошибка: Неверный формат цены.  {e}'
            except Exception as e:  # Перехватываем другие исключения
                # Обработка других исключений (SQLAlchemy и т.д.)
                db.session.rollback()  # Откат транзакции
                return f'Вы неправильно добавили товар.  Ошибка: {e}'

        return render_template('cabinet.html', email=session['email'])
    else:
        print("Email не найден в сессии")
        return redirect(url_for('index'))

@app.route('/posts')
def posts():
    product = Product.query.all()
    return render_template('posts.html', product=product)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)


# важная хрень она сохраняет отображение аккаунта во всех вкладках
@app.context_processor
def inject_user():
    return {
        'logged_in': session.get('logged_in', False),
        'email': session.get('email')
    }





