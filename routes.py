from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from app import app
from app.forms import LoginForm
import models

app = Flask(__name__)

app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FH4_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


@app.route('/')
def home():
    return render_template("home.html", page_title="WELCOME TO FH4 CARS")


@app.route('/cars')
def cars():
    cars = models.Car.query.all()
    return render_template('list_cars.html', page_title="CAR LIST",
                           cars=cars)


@app.route('/car/<int:info>')
def car(info):
    car = models.Car.query.filter_by(id=info).first_or_404()
    manufacturer = models.Manufacturer.query.filter_by(id=car.manufacturerid).first()
    title = car.name
    return render_template('show_cars.html', page_title=title, car=car, manufacturer=manufacturer)


@app.route('/manufacturers')
def manufacturers():
    manufacturers = models.Manufacturer.query.all()
    return render_template('list_manufacturers.html',
                           page_title="MANUFACTURER LIST",
                           manufacturers=manufacturers)


@app.route('/manufacturer/<int:info>')
def manufacturer(info):
    manufacturer = models.Manufacturer.query.filter(models.Manufacturer.id.in_([info])).first()
    title = manufacturer.name
    return render_template('show_manufacturers.html', page_title=title,
                           manufacturer=manufacturer)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, port=1111)
