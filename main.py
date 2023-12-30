from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import wtforms
import stripe
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, URL, Email
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = "updates"
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
stripe.api_key = 'sk_test_51NngMXSBsAMTk11HO2U2u3Fjm7Old31x4uCHgwivqg9sI8K2pReK30dVfUox9B1SocZYPQ5vs9hJUqjPZXM4kSvL00LSpVKPZB'
YOUR_DOMAIN = 'http://localhost:4242'


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
    number = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    aadhar = db.Column(db.String(250), nullable=False)




class Imp_Dates_List(db.Model):
    __tablename__ = "important_dates"
    dates = db.Column(db.String(250), nullable=False)
    occasion = db.Column(db.String(250), primary_key=True)

class Jobs_database(db.Model):
    __tablename__ = "jobs"
    title = db.Column(db.String(250), primary_key=True)
    request_from = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)

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
    number = wtforms.StringField("Number: ", validators=[DataRequired()])
    email = EmailField("Email:", validators=[DataRequired(), Email()])
    password = wtforms.PasswordField("Password: ", validators=[DataRequired()])
    aadhar =  wtforms.StringField("Aadhar number: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("submit")


class Topics(FlaskForm):
    topic = wtforms.StringField("Topic: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("Submit")


class Imp_dates(FlaskForm):
    date = wtforms.DateField("Date: ", validators=[DataRequired()])
    occasion = wtforms.StringField("Occasion: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("Submit")

class Jobs_form(FlaskForm):
    title =  wtforms.StringField("Title: ", validators=[DataRequired()])
    request_from = wtforms.StringField("From: ", validators=[DataRequired()])
    description = wtforms.StringField("Description: ", validators=[DataRequired()])
    address = wtforms.StringField("address: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("Submit")


class Jobs_delete_form(FlaskForm):
    title = wtforms.StringField("Title: ", validators=[DataRequired()])
    submit = wtforms.SubmitField("Submit")


# web pages
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/mission")
def mission():
    return render_template("mission.html")

@app.route("/donate")
def donate():
    return render_template("donate.html")

@app.route("/checkout",methods = ['POST','GET'])
def payment():
    try:

        num_list = [int(request.form['gratuity_quantity']),int(request.form['generosity_quantity']),int(request.form['graciousness_quantity'])]
        items = []
        for index,i in enumerate(num_list):
            if i>=1:
                if index == 0:
                    items.append({
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': "price_1NngfLSBsAMTk11H9lBXVEG2",
                    'quantity': i,
                })
                elif index ==1:
                    items.append({
                    'price': 'price_1NngfaSBsAMTk11Hr9elyFXE',
                    'quantity':i,
                })
                elif index == 2:
                    items.append({
                    'price': 'price_1NnglJSBsAMTk11H1Ag1tjOC',
                    'quantity': i,
                })

        checkout_session = stripe.checkout.Session.create(
            line_items=items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    form = Jobs_form()
    form2 = Imp_dates()
    form3 = Imp_dates()
    if form.validate_on_submit():
        flash("New job added")
        new_job = Jobs_database(
            title=form.title.data,
            request_from = form.request_from.data,
            description = form.description.data,
            address = form.address.data,
        )
        db.session.add(new_job)
        db.session.commit()

        return redirect(url_for('admin'))
    if form2.validate_on_submit():
        flash("New event added")
        new_date = Imp_Dates_List(
            dates = form2.date.data,
            occasion = form2.occasion.data,
        )
        db.session.add(new_date)
        db.session.commit()





    return render_template("admin.html", form=form, form2=form2, form3=form3)

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
        email_response = requests.get(
            f"https://emailvalidation.abstractapi.com/v1/?api_key=27ad0095c99c422d89802f549e633090&email={form.email.data}")

        email_response = email_response.json()
        if email_response['deliverability'] != "DELIVERABLE":
            flash("invalid email.")
            return redirect(url_for('register'))
        time.sleep(2)
        phone_response = requests.get(
            f"https://phonevalidation.abstractapi.com/v1/?api_key=43c55aa383ca446cb74891b3c25860f1&phone={form.number.data}")
        phone_response = phone_response.json()
        print(phone_response)
        if phone_response['valid'] != True:
            flash("invalid phone number.")
            return redirect(url_for('register'))

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
            number=form.number.data,
            email=form.email.data,
            password=hash_and_salted_password,
            aadhar=form.aadhar.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html", form=form)


@app.route("/home", methods=['GET', 'POST'])
def home():
        return render_template("home.html",current_user=current_user, Jobs_database=Jobs_database,
                           Imp_Dates_List=Imp_Dates_List)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    form1 = Jobs_delete_form()
    form2 = Imp_dates()
    form3 = Login()
    if form1.validate_on_submit():
        delete_jobs = Jobs_database.query.filter_by(title=form1.title.data).first()
        if not delete_jobs:
            flash("There is no such job")
        else:
            db.session.delete(delete_jobs)
            db.session.commit()
            flash("The job has been deleted")
            return redirect(url_for('admin'))
    if form2.validate_on_submit():
        delete_occasion = Imp_Dates_List.query.filter_by(occasion=form2.occasion.data).first()
        if not delete_occasion:
            flash("There is no such date")
        else:
            db.session.delete(delete_occasion)
            db.session.commit()
            flash("The event has been deleted")
            return redirect(url_for('admin'))
    if form3.validate_on_submit():
        email = form3.email.data
        password = form3.password.data
        user = User.query.filter_by(email=email).first()
        if not email == current_user.email:
            flash('This is not your email.')
            return redirect(url_for('delete'))
        if not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('delete'))
        else:
            delete_user = User.query.filter_by(id=current_user.id, email = email).first()
            db.session.delete(delete_user)
            db.session.commit()
            flash("The account has been deleted")
            return redirect(url_for('hello_world'))
    print(current_user)

    return render_template("delete.html", form1=form1, form2=form2, form3 = form3, current_user=current_user, Jobs_database=Jobs_database,
                           Imp_Dates_List=Imp_Dates_List)


if __name__ == "__main__":
    app.run(debug=True)
