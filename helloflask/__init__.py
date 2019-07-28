from datetime import datetime
from flask import Flask, url_for, render_template, request, redirect, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login = LoginManager(app)


class User(db.Model):
    __table_name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(100), default='default.png')

    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email

        self.set_password(password)

    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.email})>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Post(db.Model):
    __table_name__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Post('{self.id}', '{self.title}')>"


@app.route('/')
def home():
    logout()
    return render_template('home.html')


@app.route('/index')
def index():
    return render_template('index.html')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        session['name'] = request.form['username']
        passw = request.form['password']

        user = User.query.filter_by(username=name).first()

        if user is not None and user.check_password(passw):
            session['logged_in'] = True
            curr_user = user
            return render_template('home.html', curr_user=curr_user)
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username',None)
    return redirect(url_for('login'))


@app.route('/regi', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], email=request.form['email'], password=request.form['password'] )
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')


@app.route('/description', methods=['GET','POST'])
def description():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        users = User.query.all()
        curr_user = User.query.filter_by(username=session['name']).first()
        if request.method == 'POST':
            delete()
        return render_template('description.html', users=users, curr_user=curr_user, title='Description')


def delete():
    delete_user = User.query.filter_by(username=request.form['delete_username']).first()
    if delete_user is not None and delete_user.check_password(request.form['password']):
        db.session.delete(delete_user)
        db.session.commit()
        if request.form['delete_username'] == session['name']:
            logout()
            return redirect(url_for('description'))
        return redirect(url_for('description'))


@app.route('/about')
def about():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        posts = Post.query.all()
        return render_template('about.html', posts=posts, title='About')


@app.route('/about1')
def about1():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('about1.html', title='About1')

