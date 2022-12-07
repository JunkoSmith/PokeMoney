from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap


from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedata.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(5), nullable=False)
    detail = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

@login_manager.user_loader
def load_uder(user_id):
    return User.query.get(int(user_id))
        

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
      username = request.form.get('username')
      password = request.form.get('password')

      user = User(username=username, password=generate_password_hash(password, method='sha256'))

      db.session.add(user)
      db.session.commit()
      return redirect(url_for("login"))
    else:
      return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
      username = request.form.get('username')
      password = request.form.get('password')

      user = User.query.filter_by(username=username).first()
      if check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for("record"))
        
    else:
        return render_template('login.html')


@app.route('/record', methods=['GET', 'POST'])
@login_required
def record():
    if request.method == "POST":
      create = request.form.get('create')
      title = request.form.get('title')
      detail = request.form.get('detail')

      create = datetime.strptime(create, '%Y-%m-%d')
      post = Post(create=create, title=title, detail=detail)

      db.session.add(post)
      db.session.commit()
      return redirect(url_for("create"))

    else:
      return render_template('record.html')

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
      posts = Post.query.order_by(Post.create).all()
      return render_template('create.html', posts=posts)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
      return render_template('update.html', post=post)
    else:
      post.create = datetime.strptime(request.form.get('create'), '%Y-%m-%d')
      post.title = request.form.get('title')
      post.detail = request.form.get('detail')
      #reflect canges to db
      db.session.commit()
      #go to top page
      return redirect(url_for("create"))


@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("create"))
    
# after Flask 2.3   
if __name__ == ('__main__'):
  app.run(debug=True, host='0.0.0.0', port=5050)