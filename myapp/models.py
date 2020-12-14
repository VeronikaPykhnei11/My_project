from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/nika/PycharmProjects/LABA_4_PP/cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


class Film(db.Model):
    __tablename__ = 'Film'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Float(), nullable=False)
    rating = db.Column(db.Float(), nullable=False)
    records = db.relationship('Records', backref='Film', uselist=False, lazy='joined')
    def repr(self):
        return '<Film %r' % self.title


class Hall(db.Model):
    __tablename__ = 'Hall'
    id = db.Column(db.Integer(), primary_key=True)
    opacity = db.Column(db.Integer(), nullable=False)
    records = db.relationship('Records', backref='Hall', uselist=False, lazy='joined')

    def repr(self):
        return "Hall: {} - {}>".format(id, self.opacity)


class Admin(db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer(), primary_key=True)
    nickname = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    timetable = relationship('Timetable', backref='Admin', uselist=False, lazy='joined')

    def repr(self):
        return "Admin: {} - {} {}>".format(id, self.firstname, self.lastname)


class Timetable(db.Model):
    __tablename__ = 'Timetable'
    id = db.Column(db.Integer(), primary_key=True)
    Admin_id = db.Column(db.Integer, ForeignKey('Admin.id'))
    records = db.relationship('Records', backref='Timetable', uselist=False, lazy='joined')


class Records(db.Model):
    __tablename__ = 'Records'
    id = db.Column(db.Integer(), primary_key=True)
    timetable_id = db.Column(db.Integer, ForeignKey('Timetable.id'))
    film_id = db.Column(db.Integer, ForeignKey('Film.id'))
    hall_id = db.Column(db.Integer, ForeignKey('Hall.id'))

if __name__ == '__main__':
    manager.run()