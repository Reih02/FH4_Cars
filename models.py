from routes import db


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


class Manufacturer(db.Model):
    __tablename__ = 'Manufacturer'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.Text(50), nullable=False)
    details = db.Column(db.Text(250), nullable=False)
