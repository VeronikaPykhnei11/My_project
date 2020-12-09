from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/nika/PycharmProjects/LABA_4_PP/cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

film_hall = db.Table('film_hall',
        db.Column('film_id', db.Integer, db.ForeignKey('Film.id'), primary_key=True),
        db.Column('hall_id', db.Integer, db.ForeignKey('Hall.id'), primary_key=True)
)

film_timetable = db.Table('film_timetable',
            db.Column('film_id', db.Integer, db.ForeignKey('Film.id'), primary_key=True),
            db.Column('timetable_id', db.Integer, db.ForeignKey('Timetable.id'), primary_key=True)
)

hall_timetable = db.Table('hall_timetable',
            db.Column('hall_id', db.Integer, db.ForeignKey('Hall.id'), primary_key=True),
            db.Column('timetable_id', db.Integer, db.ForeignKey('Timetable.id'), primary_key=True)
)


class Film(db.Model):
    __tablename__ = 'Film'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Float(), nullable=False)
    rating = db.Column(db.Float(), nullable=False)
    halls = db.relationship('Hall', secondary=film_hall, lazy='subquery',
                           backref=db.backref('Film', lazy=True))
    def repr(self):
        return '<Film %r' % self.title


class Hall(db.Model):
    __tablename__ = 'Hall'
    id = db.Column(db.Integer(), primary_key=True)
    opacity = db.Column(db.Integer(), nullable=False)


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
    timetables = db.relationship('Timetable', backref='Admin')

    def repr(self):
        return "Admin: {} - {} {}>".format(id, self.firstname, self.lastname)


class Timetable(db.Model):
    __tablename__ = 'Timetable'
    id = db.Column(db.Integer(), primary_key=True)
    Admin_id = db.Column(db.Integer(), db.ForeignKey('Admin.id'))
    films = db.relationship('Film', secondary=film_timetable, lazy='subquery',
                            backref=db.backref('Timetable', lazy=True))
    halls = db.relationship('Hall', secondary=hall_timetable, lazy='subquery',
                            backref=db.backref('Timetable', lazy=True))


if __name__ == '__main__':
    manager.run()