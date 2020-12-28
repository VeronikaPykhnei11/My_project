from flask import Flask, request, Response, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, pre_load
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy import ForeignKey
from flask_jwt import jwt_required, JWT, current_identity

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/nika/PycharmProjects/LABA_4_PP/cinema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_AUTH_URL_RULE'] = '/admin/login'
app.config['JWT_AUTH_HEADER_PREFIX'] = 'Bearer'
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


def authenticate(username, password):
    user = Admin.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user


def identity(payload):
    user_id = payload['identity']
    return Admin.query.get(user_id)


jwt = JWT(app, authenticate, identity)


##### MODELS #####
class Film(db.Model):
    __tablename__ = 'Film'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Float(), nullable=False)
    rating = db.Column(db.Float(), nullable=False)
    records = db.relationship('Timetable', backref='Film', uselist=False, lazy='joined')

    def repr(self):
        return '<Film %r' % self.title


class Hall(db.Model):
    __tablename__ = 'Hall'
    id = db.Column(db.Integer(), primary_key=True)
    opacity = db.Column(db.Integer(), nullable=False)
    records = db.relationship('Timetable', backref='Hall', uselist=False, lazy='joined')

    def repr(self):
        return "Hall: {} - {}>".format(id, self.opacity)


class Admin(db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def repr(self):
        return "Admin: {} - {} {}>".format(id, self.firstname, self.lastname)


class Timetable(db.Model):
    __tablename__ = 'Timetable'
    id = db.Column(db.Integer(), primary_key=True)
    num_of_record = db.Column(db.Integer(), nullable=False)
    film_id = db.Column(db.Integer, ForeignKey('Film.id'))
    hall_id = db.Column(db.Integer, ForeignKey('Hall.id'))


##### SCHEMAS #####


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class FilmSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=must_not_be_blank)
    duration = fields.Float(required=True, validate=must_not_be_blank)
    rating = fields.Float(required=True, validate=must_not_be_blank)

    def format_film(self, film):
        return "Title - {}, duration - {}, rating - {}".format(film.title, film.duration, film.rating)


class HallSchema(Schema):
    id = fields.Int(dump_only=True)
    opacity = fields.Int(required=True, validate=must_not_be_blank)

    def format_hall(self, hall):
        return "Hall ID: {}, opacity: {}".format(hall.id, hall.opacity)


class AdminSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=must_not_be_blank)
    firstname = fields.Str(required=True, validate=must_not_be_blank)
    lastname = fields.Str(required=True, validate=must_not_be_blank)
    email = fields.Email(required=True, validate=must_not_be_blank)
    phone = fields.Str(required=True, validate=must_not_be_blank)
    password = fields.Str(required=True, validate=must_not_be_blank)

    def format_admin(self, admin):
        return "Admin: name - {} {}, username - {}, email - {}, phone - {}".format(admin.firstname, admin.lastname,
                                                                                   admin.username, admin.email,
                                                                                   admin.phone)


class TimetableSchema(Schema):
    id = fields.Int(dump_only=True)
    num_of_record = fields.Int(required=True, validate=must_not_be_blank)
    film_id = fields.Int(required=True, validate=must_not_be_blank)
    hall_id = fields.Int(required=True, validate=must_not_be_blank)


film_schema = FilmSchema()
film_schema_put = FilmSchema(only=("id", "rating"))
hall_schema = HallSchema()
hall_schema_put = HallSchema(only=("id", "opacity"))
admin_schema = AdminSchema()
admins_schema = AdminSchema(only=("id", "username"))
timetable_schema = TimetableSchema()
timetables_schema = TimetableSchema(only=("id", "film_id"))


@app.route('/api/v1/hello-world-<int:variant>')
def hello_world(variant):
    return 'Hello World ' + str(variant) + "!"


@app.route('/')
def main_page():
    return 'My Project'


@app.route('/film', methods=['POST'])
@jwt_required()
def film_post():
    json = request.json
    if not json:
        return {"message": "No input data provided"}, 404
    if request.method == 'POST':
        try:
            data = film_schema.load(json)
        except ValidationError as e:
            return e.messages, 422
        title = data['title']
        duration = data['duration']
        rating = data['rating']
        film1 = Film(title=title, duration=duration, rating=rating)
        db.session.add(film1)
        db.session.commit()
        return {"message": "Success"}, 200


@app.route('/film/<int:film_id>', methods=['GET'])
def film_get_by_id(film_id):
    film = Film.query.get(film_id)
    if not film:
        return {"message": "Film could not be found"}, 404
    if request.method == 'GET':
        film = Film.query.get(film_id)
        return 'Film: title - {}, duration - {}, rating - {}'.format(film.title, film.duration, film.rating), 200


@app.route('/film/<int:film_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def film_by_id(film_id):
    film = Film.query.get(film_id)
    if not film:
        return {"message": "Film could not be found"}, 404
    if request.method == 'PUT':
        json = request.json
        if not json:
            return {"message": "No input data provided"}, 404
        try:
            data = film_schema_put.load(json)
        except ValidationError as e:
            return e.messages, 422
        rating = data['rating']
        db.session.query(Film).filter(Film.id == film_id).update({'rating': rating})
        db.session.commit()
        return {"message": "Success"}, 200
    elif request.method == 'DELETE':
        db.session.delete(film)
        db.session.commit()
        return {"message": "Success"}, 200


@app.route('/hall', methods=['POST'])
@jwt_required()
def hall_post():
    json = request.json
    if not json:
        return {"message": "No input data provided"}, 404
    elif request.method == 'POST':
        try:
            data = hall_schema.load(json)
        except ValidationError as e:
            return e.messages, 422
        opacity = data['opacity']
        hall1 = Hall(opacity=opacity)
        db.session.add(hall1)
        db.session.commit()
        return {"message": "Success"}, 200

@app.route('/hall/<int:hall_id>', methods=['GET'])
def hall_get_by_id(hall_id):
    hall = Hall.query.get(hall_id)
    if not hall:
        return {"message": "Hall could not be found"}, 404
    if request.method == 'GET':
        return 'Hall: opacity - {}'.format(hall.opacity), 200

@app.route('/hall/<int:hall_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def hall_by_id(hall_id):
    hall = Hall.query.get(hall_id)
    if not hall:
        return {"message": "Hall could not be found"}, 404
    if request.method == 'PUT':
        json = request.json
        if not json:
            return {"message": "No input data provided"}, 404
        try:
            data = hall_schema_put.load(json)
        except ValidationError as e:
            return e.messages, 422
        opacity = data['opacity']
        db.session.query(Hall).filter(Hall.id == hall_id).update({'opacity': opacity})
        db.session.commit()
        return {"message": "Success"}, 200
    elif request.method == 'DELETE':
        db.session.delete(hall)
        db.session.commit()
        return {"message": "Success"}, 200


@app.route('/admin', methods=['POST'])
def admin_post():
    json = request.json
    if not json:
        return {"message": "No input data provided"}, 404
    if request.method == 'POST':
        try:
            data = admin_schema.load(json)
        except ValidationError as e:
            return e.messages, 422
        username = data['username']
        firstname = data['firstname']
        lastname = data['lastname']
        email = data['email']
        password = data['password']
        pass_hash = bcrypt.generate_password_hash(password)
        phone = data['phone']
        admin1 = Admin(username=username, firstname=firstname, lastname=lastname, email=email, phone=phone,
                       password=pass_hash)
        db.session.add(admin1)
        db.session.commit()
        return {"message": "Success"}, 200


@app.route('/admin/<int:admin_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def admin_by_id(admin_id):
    admin = Admin.query.get(admin_id)
    if not admin:
        return {"message": "Admin could not be found"}, 404
    if request.method == 'GET':
        return 'Admin: id - {}, username - {}, firstname - {}, lastname - {}'.format(admin_id, admin.username,
                                                                                     admin.firstname,
                                                                                     admin.lastname), 200
    elif request.method == 'PUT':
        if current_identity.id != admin_id:
            return {"message": "Forbidden"}, 403
        json = request.json
        if not json:
            return {"message": "No input data provided"}, 404
        try:
            data = admins_schema.load(json)
        except ValidationError as e:
            return e.messages, 422
        username = data['username']
        db.session.query(Admin).filter(Admin.id == admin_id).update({'username': username})
        db.session.commit()
        return {"message": "Success"}, 200
    elif request.method == 'DELETE':
        if current_identity.id != admin_id:
            return {"message": "Forbidden"}, 403
        db.session.delete(admin)
        db.session.commit()
        return {"message": "Success"}, 200


@app.route('/timetable', methods=['POST'])
@jwt_required()
def timetable_post():
    json = request.json
    if not json:
        return {"message": "No input data provided"}, 404
    if request.method == 'POST':
        try:
            data = timetable_schema.load(json)
        except ValidationError as e:
            return e.messages, 422
        num_of_record = data['num_of_record']
        film_id = Film.query.filter_by(id=data['film_id']).first()
        if film_id is None:
            return {"message": "Film could not be found"}, 404
        hall_id = Hall.query.filter_by(id=data['hall_id']).first()
        if hall_id is None:
            return {"message": "Hall could not be found"}, 404
        t1 = Timetable(num_of_record=num_of_record, film_id=data['film_id'], hall_id=data['hall_id'])
        db.session.add(t1)
        db.session.commit()
        return {"message": "Success"}, 200


@app.route('/timetable/<int:timetable_id>', methods=['GET'])
def timetable_get_by_id(timetable_id):
    timetable = Timetable.query.get(timetable_id)
    if not timetable:
        return {"message": "Timetable could not be found"}, 404
    if request.method == 'GET':
        timetable = Timetable.query.get(timetable_id)
        return "Timetable id: {}, film-{}, hall-{}".format(timetable_id, timetable.film_id, timetable.hall_id), 200

@app.route('/timetable/<int:timetable_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def timetable_by_id(timetable_id):
    timetable = Timetable.query.get(timetable_id)
    if not timetable:
        return {"message": "Timetable could not be found"}, 404
    if request.method == 'PUT':
        json = request.json
        if not json:
            return {"message": "No input data provided"}, 404
        try:
            data = timetables_schema.load(json)
        except ValidationError as e:
            return e.messages, 422
        film_id = Film.query.filter_by(id=data['film_id']).first()
        if film_id is None:
            return {"message": "Film could not be found"}, 404
        db.session.query(Timetable).filter(Timetable.id == timetable_id).update({'film_id': data['film_id']})
        db.session.commit()
        return {"message": "Success"}, 200
    elif request.method == 'DELETE':
        db.session.delete(timetable)
        db.session.commit()
        return {"message": "Success"}, 200


if __name__ == '__main__':
    app.run()