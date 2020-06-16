from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import models
from forms import LoginForm, RegistrationForm
from flask_login import logout_user, login_user, LoginManager, current_user

# initialisation stuff
app = Flask(__name__)

app.config['SECRET_KEY'] = 'reilly_is_cool'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FH4_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
loginTest = LoginManager(app)
loginTest.login_view = 'login'
# ---------------------


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
    return render_template('show_cars.html', page_title=title, car=car,
                           manufacturer=manufacturer)


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



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = models.User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


#@app.route('/profile')
#@login_required
#def profile():


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@loginTest.user_loader
def load_user(id):
    return models.User.query.get(int(id))


if __name__ == "__main__":
    app.run(debug=True, port=1111)
