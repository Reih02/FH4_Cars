from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import models

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FH4_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
def home():
    return render_template("home.html", page_title="WELCOME TO FH4 CARS")


@app.route('/cars')
def cars():
    cars = models.Car.query.all()
    return render_template('list_cars.html', page_title="CAR LIST",
                           cars=cars)


@app.route('/cars/<int:id>')
def car(id):
    car = models.Car.query.filter_by(id=id).first()
    title = car.name
    return render_template('show_cars.html', page_title=title,
                           car=car)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, port=1111)
