from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import os


def test_index_page(client):
   response = client.get('/')

   assert response.status_code == 200
   assert b'Welcome!' in response.data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedata.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_uder(user_id):
    return User.query.get(int(user_id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(5), nullable=False)
    detail = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)

class SignupForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Signup")

    def validate_username(self, username):
      existing_user_username = User.query.filter_by(username=username.data).first()

      if existing_user_username:
        raise ValidationError(
          "That user name already exist. please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Login")          


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
      hashed_password = bcrypt.generate_password_hash(form.password.data)
      new_user = User(username=form.username.data, password=hashed_password)
      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for("login"))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(username=form.username.data).first()
      if user:
        if bcrypt.check_password_hash(user.password, form.password.data):
          login_user(user)
          return redirect(url_for("record"))

    return render_template('login.html', form=form)


@app.route('/record', methods=['GET', 'POST'])
@login_required
def record(): #dash bord
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


@app.route('/create', methods=['GET', 'POST']) #get=access to the web page
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
      #go to update page
    else:
      post.title = request.form.get('title')
      post.detail = request.form.get('detail')
      post.create = datetime.strptime(request.form.get('create'), '%Y-%m-%d')
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
  app.run()