from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)

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
        mail = request.form['email']
        password = request.form['password']

        post = Post(title=mail, text=password) #запись данных

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/index')  # переадресация на страницу
        except:
            return 'При добавлении данных произошла ошибка'
    else:
        return render_template('sign_in.html')

@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)