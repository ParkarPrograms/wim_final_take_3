from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import wtforms
import os
from dotenv import load_dotenv
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, URL, Email
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("KEY")
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "login_information"
    id = db.Column(db.String(250), primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


class Topics_list(db.Model):
    __tablename__ = "news_topics"
    id = db.Column(db.String(250), primary_key=True)
    topic = db.Column(db.String(250), primary_key=True)


class Imp_Dates_List(db.Model):
    __tablename__ = "important_dates"
    id = db.Column(db.String(250), primary_key=True)
    dates = db.Column(db.String(250), primary_key=True)
    occasion = db.Column(db.String(250), primary_key=True)


with app.app_context():
    db.create_all()


# forms
class Login(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = wtforms.PasswordField(validators=[DataRequired()])
    submit = wtforms.SubmitField("submit")


class Register(FlaskForm):
    user_id = wtforms.StringField("User ID: ", validators=[DataRequired()])
    name = wtforms.StringField("Name: ", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = wtforms.PasswordField("Password: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("submit")


class Topics(FlaskForm):
    topic = wtforms.StringField("Topic: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("Submit: ")


class Imp_dates(FlaskForm):
    date = wtforms.DateField("Date: ", validators=[DataRequired()])
    occasion = wtforms.StringField("Occasion: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("Submit: ")


# web pages
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:

            login_user(user)
        return redirect(url_for('home'))
    return render_template("login.html", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        if User.query.filter_by(id = form.user_id.data).first():
            flash("ID already taken. Please Try another one")
            return redirect(url_for('register'))
        if User.query.filter_by(email=form.email.data).first():
            flash("You have already registered. Log in instead.")
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            id=form.user_id.data,
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html", form=form)


@app.route("/home", methods=['GET', 'POST'])
def home():
    form1 = Topics()
    form2 = Imp_dates()
    if form1.validate_on_submit():
        new_topic = Topics_list(
            id=current_user.id,
            topic=form1.topic.data.strip().lower()
        )
        db.session.add(new_topic)
        db.session.commit()
        flash("your new topic has been added!")
        return redirect(url_for('home'))
    if form2.validate_on_submit():
        new_occasion = Imp_Dates_List(
            id=current_user.id,
            dates=form2.date.data,
            occasion=form2.occasion.data.strip().lower()
        )
        db.session.add(new_occasion)
        db.session.commit()
        flash("your new date has been added!")
        return redirect(url_for('home'))
    print(current_user)

    return render_template("home.html", form1=form1, form2=form2, current_user=current_user, Topics_list=Topics_list,
                           Imp_Dates_List=Imp_Dates_List)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    form1 = Topics()
    form2 = Imp_dates()
    if form1.validate_on_submit():
        delete_topic = Topics_list.query.filter_by(id=current_user.id, topic=form1.topic.data.strip().lower()).first()
        if not delete_topic:
            flash("There is no such topic")
        else:
            db.session.delete(delete_topic)
            db.session.commit()
            flash("your topic has been deleted")
            return redirect(url_for('home'))
    if form2.validate_on_submit():
        delete_occasion = Imp_Dates_List.query.filter_by(id=current_user.id, dates=form2.date.data,
                                                         occasion=form2.occasion.data.strip().lower()).first()
        if not delete_occasion:
            flash("There is no such date in your account")
        else:
            db.session.delete(delete_occasion)
            db.session.commit()
            flash("your occasion has been deleted")
            return redirect(url_for('home'))
    print(current_user)

    return render_template("delete.html", form1=form1, form2=form2, current_user=current_user, Topics_list=Topics_list,
                           Imp_Dates_List=Imp_Dates_List)


if __name__ == "__main__":
    app.run(debug=True)
