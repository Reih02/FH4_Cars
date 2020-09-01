from routes import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt


# defines rows in Car table
class Car(db.Model):
    __tablename__ = 'Car'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.Text(50), nullable=False)
    horsepower = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Text, nullable=False)
    wheeldrive = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text)
    manufacturerid = db.Column(db.Text, db.ForeignKey('Manufacturer.id'))


# defines rows in Manufacturer table
class Manufacturer(db.Model):
    __tablename__ = 'Manufacturer'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.Text(50), nullable=False)
    details = db.Column(db.Text(250), nullable=False)


# defines rows in User table
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128))

    # tells Python how to print objects of this class for debugging purposes
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # encoding token using sha256 algorithm
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


# defines rows in UserCar table
class UserCar(db.Model):
    __tablename__ = 'UserCar'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.ForeignKey('User.id'))
    cid = db.Column(db.ForeignKey('Car.id'))
