from flask import Flask, render_template, flash, redirect, url_for, request, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.urls import url_parse
import models
from forms import LoginForm, RegistrationForm, SearchForm
from flask_login import logout_user, login_user, LoginManager, current_user, login_required
from flask_mail import Mail
from forms import ResetPasswordRequestForm, ResetPasswordForm

# initialisation stuff
app = Flask(__name__)

# defines secret key for use in anything encrypted(logins, password hashing, etc.)
app.config['SECRET_KEY'] = 'vr2YEHkNyPsuF3TdFMsL5a67veTPBtjrfx5FrdRLky5TQf3wAL'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FH4_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = 1
app.config['MAIL_USERNAME'] = 'reillyhaskins@gmail.com'
app.config['MAIL_PASSWORD'] = 'pamrxmhwpfvgsoxb'
app.config['ADMINS'] = 'reillyhaskins@gmail.com'

db = SQLAlchemy(app)
loginTest = LoginManager(app)
loginTest.login_view = 'login'

mail = Mail(app)
# ---------------------
# had to put this import down here because it somehow made the import work
from email1 import send_password_reset_email

# defines searchform for use in search functions
@app.context_processor
def inject_search():
    searchform = SearchForm()
    return dict(searchform=searchform)

# home route (where users land upon visit)
@app.route('/')
def home():
    return render_template("home.html", page_title="WELCOME TO FH4 CARS")


# route to show all cars
@app.route('/cars', methods=['GET', 'POST'])
def cars():
    cars = models.Car.query.all()
    # defines search form under form variable for use later
    form = SearchForm()
    # if search form validates:
    if form.validate_on_submit():
        # run next route (carsearch)
        return redirect(url_for('carsearch', search=form.query.data))
        flash("Search too long")
    else:
        # go back
        return render_template('list_cars.html', page_title="CAR LIST",
                               cars=cars)

# route to show a user's searched car matches
@app.route('/carsearch/<search>', methods=['GET', 'POST'])
def carsearch(search):
    # get car names from the database like that of the search input
    # (using SQLAlchemy's built-in algorithm)
    car = models.Car.query.filter(models.Car.name.ilike('%{}%'.format(search))).all()
    print(car)
    # returs name of cars in a loop as there are usually multiple results
    for i in car:
        print(i.name)
    return render_template('csearch.html', page_title="YOUR SEARCH", car=car)


# route to show info on the car the user selects/clicks
@app.route('/car/<int:info>', methods=['GET', 'POST'])
def car(info):
    car = models.Car.query.filter_by(id=info).first_or_404()
    # gets the manufacturer that made the car
    manufacturer = models.Manufacturer.query.filter_by(id=car.manufacturerid).first()
    title = car.name
    # used following try & except in order to work around the attribute error
    # I was getting if the car was not favourited by user
    try:
        favourited = models.UserCar.query.filter_by(uid=current_user.id, cid=info).all()
    except AttributeError:
        favourited = None
    return render_template('show_cars.html', page_title=title, car=car,
                           manufacturer=manufacturer,
                           favourited=favourited)


# route to add favourite car to user's profile
@app.route('/favourite/<int:id>', methods=['GET', 'POST'])
@login_required
def favourite(id):
    # adds favourite car by assigning the current user's id to the uid table,
    # and the car's id to the cid table
    is_favourited = models.UserCar.query.filter_by(uid=current_user.id, cid=id).first()
    if is_favourited is None:
        try:
            favourite_car = models.UserCar(uid=current_user.id, cid=id)
            db.session.add(favourite_car)
            db.session.commit()
        except:
            abort(500)
    return redirect(url_for('car', info=id))


# route to delete a favourite car from a user's profile
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    # deletes favourite car by getting the car where uid is the current user's
    # id and the cid is the current car's id in the favourited car table,
    # and removing it from the database
    try:
        favourite_car = db.session.query(models.UserCar).filter_by(uid=current_user.id, cid=id).first_or_404()
        db.session.delete(favourite_car)
        db.session.commit()
    except:
        redirect(url_for('car', info=id))
    return redirect(url_for('car', info=id))


# route to show all manufacturers
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


# route to show all matches for a user's search on the manufacturer page
@app.route('/manufacturersearch/<search>', methods=['GET', 'POST'])
def manufacturersearch(search):
    manufacturer = models.Manufacturer.query.filter(models.Manufacturer.name.ilike('%{}%'.format(search))).all()
    print(manufacturer)
    for i in manufacturer:
        print(i.name)
    return render_template('msearch.html', page_title="YOUR SEARCH",
                           manufacturer=manufacturer)


# route that shows more info on the manufacturer the user opened
@app.route('/manufacturer/<int:info>')
def manufacturer(info):
    manufacturer = models.Manufacturer.query.filter_by(id=info).first()
    # gets cars manufacturer made by getting all cars that have the
    # same manufacturer id as the current manufacturer's id
    cars = models.Car.query.filter_by(manufacturerid=manufacturer.id).all()
    title = manufacturer.name
    return render_template('show_manufacturers.html', page_title=title,
                           manufacturer=manufacturer, cars=cars)


# route to handle logins for the user
@app.route('/login', methods=['GET', 'POST'])
def login():
    # redirect users back if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    # if form works:
    if form.validate_on_submit():
        # checks if username is in the database
        user = models.User.query.filter_by(username=form.username.data).first()
        # if it doesn't exist yet:
        if user is None or not user.check_password(form.password.data):
            # tell user login didn't work and go back to login page
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # gets contents of flask's request variable that contains all the info
        # that the user sent with their request
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # sends users home if nothing obtained from form
            next_page = url_for('home')
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)


# route to handle sign ups for the user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # sends users home if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # puts username, email, and password into the database
        user = models.User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # tells user they are signed up and sends them to login page
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign up', form=form)


# route to handle logging out for the user
@app.route('/logout')
def logout():
    # uses flask's built-in logout feature and sends user's home after
    # logging out
    logout_user()
    return redirect(url_for('home'))


# route that shows the user's current profile (if logged in)
@app.route('/profile/<username>')
def profile(username):
    # if user is not signed in:
    if current_user.is_anonymous:
        # tell user to log in before going to their profile, and sends them home
        flash("Please log in or sign up before attempting to view your profile!")
        return redirect(url_for('home'))
    # gets the corresponding info from database for the current user
    profile = models.User.query.filter_by(username=username).first_or_404()
    favcars = models.UserCar.query.filter_by(uid=current_user.id).all()
    # puts user's favourite cars in a temporary list in order to call
    # everything that applies, and then calls from list (only working way I
    # could implement this function)
    templist = []
    for i in favcars:
        templist.append(i.cid)
    cars = models.Car.query.filter(models.Car.id.in_(templist)).all()
    return render_template('profile.html', title='Your Profile',
                           profile=profile, cars=cars)

# route to send email to user with link to reset password page
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # if user is already logged in:
    if current_user.is_authenticated:
        # send user home
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        # gets email to send password reset to and sends
        user = models.User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # tells user to check email for reset password link and sends them to
        # login page
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


# route to reset password (link to route obtained from email)
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # if user is already logged in:
    if current_user.is_authenticated:
        # send them home
        return redirect(url_for('home'))
    user = models.User.verify_reset_password_token(token)
    # if token can't be verified to being requested by current user:
    if not user:
        # send them home
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # updates the username and password info in the database
        user.set_password(form.password.data)
        db.session.query(models.User).filter_by(id=user.id).update({models.User.password_hash: user.password_hash})
        db.session.commit()
        # tells user they have reset password successfully and sends them to
        # login page
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# error handler for a 404 error (returns 404.html instead of standard 404 page)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


# error handler for a 500 error (returns 500.html instead of standard 500 page)
@app.errorhandler(500)
def internal_server(e):
    return render_template("500.html")


# keeps track of user by storing id when they visit a page, and then uses this
# id to load the user into memory
@loginTest.user_loader
def load_user(id):
    return models.User.query.get(int(id))


# tells flask what port to run on
if __name__ == "__main__":
    app.run(debug=True, port=1111)
