from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.urls import url_parse
import models
from forms import LoginForm, RegistrationForm, SearchForm
from flask_login import logout_user, login_user, LoginManager, current_user, login_required
from flask_mail import Mail
from forms import ResetPasswordRequestForm, ResetPasswordForm

# initialisation stuff
app = Flask(__name__)

app.config['SECRET_KEY'] = 'vr2YEHkNyPsuF3TdFMsL5a67veTPBtjrfx5FrdRLky5TQf3wAL'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FH4_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = 1
app.config['MAIL_USERNAME'] = 'reillyhaskins@gmail.com'
app.config['MAIL_PASSWORD'] = 'WqYjJr02'
app.config['ADMINS'] = 'reillyhaskins@gmail.com'

db = SQLAlchemy(app)
loginTest = LoginManager(app)
loginTest.login_view = 'login'

mail = Mail(app)
# ---------------------
from email1 import send_password_reset_email

# defines searchform for use in search functions
@app.context_processor
def inject_search():
    searchform = SearchForm()
    return dict(searchform=searchform)


@app.route('/')
def home():
    return render_template("home.html", page_title="WELCOME TO FH4 CARS")


@app.route('/cars', methods=['GET', 'POST'])
def cars():
    form = SearchForm()
    cars = models.Car.query.all()
    # if search form validates:
    if form.validate_on_submit():
        # run next route (carsearch)
        return redirect(url_for('carsearch', search=form.query.data))
    else:
        return render_template('list_cars.html', page_title="CAR LIST",
                               cars=cars)


@app.route('/carsearch/<search>', methods=['GET', 'POST'])
def carsearch(search):
    car = models.Car.query.filter(models.Car.name.ilike('%{}%'.format(search))).all()
    print(car)
    for i in car:
        print(i.name)
    return render_template('csearch.html', page_title="YOUR SEARCH", car=car)


@app.route('/car/<int:info>', methods=['GET', 'POST'])
def car(info):
    #form = FavouriteCarForm()
    car = models.Car.query.filter_by(id=info).first_or_404()
    manufacturer = models.Manufacturer.query.filter_by(id=car.manufacturerid).first()
    title = car.name
    if not current_user.is_authenticated:
        flash("Please log in to favourite this car")
        return redirect(url_for('car', info=info))
    favourited = models.UserCar.query.filter_by(uid=current_user.id, cid=info).all()
    return render_template('show_cars.html', page_title=title, car=car,
                           manufacturer=manufacturer,
                           favourited=favourited)


@app.route('/favourite/<int:id>', methods=['GET', 'POST'])
@login_required
def favourite(id):
    favourite_car = models.UserCar(uid=current_user.id, cid=id)
    db.session.add(favourite_car)
    db.session.commit()
    return redirect(url_for('car', info=id))


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    favourite_car = db.session.query(models.UserCar).filter_by(uid=current_user.id, cid=id).first_or_404()
    db.session.delete(favourite_car)
    db.session.commit()
    return redirect(url_for('car', info=id))


@app.route('/manufacturers', methods=['GET', 'POST'])
def manufacturers():
    form = SearchForm()
    manufacturers = models.Manufacturer.query.all()
    if form.validate_on_submit():
        return redirect(url_for('manufacturersearch', search=form.query.data))
    else:
        return render_template('list_manufacturers.html',
                               page_title="MANUFACTURER LIST",
                               manufacturers=manufacturers)


@app.route('/manufacturersearch/<search>', methods=['GET', 'POST'])
def manufacturersearch(search):
    manufacturer = models.Manufacturer.query.filter(models.Manufacturer.name.ilike('%{}%'.format(search))).all()
    print(manufacturer)
    for i in manufacturer:
        print(i.name)
    return render_template('msearch.html', page_title="YOUR SEARCH",
                           manufacturer=manufacturer)


@app.route('/manufacturer/<int:info>')
def manufacturer(info):
    manufacturer = models.Manufacturer.query.filter_by(id=info).first()
    cars = models.Car.query.filter_by(manufacturerid=manufacturer.id).all()
    title = manufacturer.name
    return render_template('show_manufacturers.html', page_title=title,
                           manufacturer=manufacturer, cars=cars)


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
        user = models.User(username=form.username.data, email=form.email.data)
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


@app.route('/profile/<username>')
@login_required
def profile(username):
    profile = models.User.query.filter_by(username=username).first_or_404()
    favcars = models.UserCar.query.filter_by(uid=current_user.id).all()
    templist = []
    for i in favcars:
        templist.append(i.cid)
    cars = models.Car.query.filter(models.Car.id.in_(templist)).all()
    return render_template('profile.html', title='Your Profile',
                           profile=profile, cars=cars)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = models.User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@loginTest.user_loader
def load_user(id):
    return models.User.query.get(int(id))


if __name__ == "__main__":
    app.run(debug=True, port=1111)
