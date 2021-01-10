import json
import pytest
import datetime
import flask_jwt


from myapp.app import app as flaskapp
from myapp.app import jwt, Admin, Hall, Timetable, Film, db


@pytest.fixture
def app():
    yield flaskapp


@pytest.fixture
def client(app):
    return flaskapp.test_client()


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    Admin.query.delete()
    Hall.query.delete()
    Timetable.query.delete()
    Film.query.delete()


token = None


def fake_func(t):
    print(t)
    return True

@pytest.fixture()
def login():
    app.app_context().push()
    app.testing = True
    admin1 = app.test_client()
    global token
    admin_id = Admin.query.filter_by(username="John").first().id
    time_limit = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    payload = {"id": admin_id, "exp": time_limit}
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    yield admin1
    app.testing = False


def test_main(client):
    res = client.get('/')
    assert res.status_code == 200
    expected = 'My Project'
    assert expected == json.loads(res.get_data(as_text=True))


def test_hello_world(app, client):
    res = client.get('/api/v1/hello-world-16')
    assert res.status_code == 200
    expected = 'Hello World 16!'
    assert expected == json.loads(res.get_data(as_text=True))


def test_film_post1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'title': '123', 'duration': 1.5, 'rating': 3.8}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/film', json=data, headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_film_post2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'title': 123, 'duration': 1.5, 'rating': 3.8}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/film', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'title': ['Not a valid string.']}
    assert expected == json.loads(t1.get_data())


def test_film_post3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/film', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_film_get1():
    res = flaskapp.test_client().get('/film/4477')
    assert res.status_code == 404
    expected = {'message': 'Film could not be found'}
    assert expected == json.loads(res.get_data())


def test_film_get2():
    res = flaskapp.test_client().get('/film/4')
    assert res.status_code == 200
    expected = b"Film: title - 123, duration - 1.5, rating - 3.8"
    assert expected == res.get_data()


def test_film_put1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'rating': 3.8}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/film/5655', json=data, headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Film could not be found'}
    assert expected == json.loads(t1.get_data())


def test_film_put2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'rating': 3.8}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/film/2', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_film_put3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'rating': "ert"}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/film/2', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'rating': ['Not a valid number.']}
    assert expected == json.loads(t1.get_data())


def test_film_put4(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'rating': 5.0}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/film/2', json=data, headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_film_delete1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().delete('/film/777', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Film could not be found'}
    assert expected == json.loads(t1.get_data())


def test_film_delete2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    if Film.query.filter_by(id=3).first() is None:
        f1 = Film(id=3, title='aa', duration=3.5, rating=4.0)
        db.session.add(f1)
        db.session.commit()
    t1 = flaskapp.test_client().delete('/film/3', headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_hall_post1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'opacity': 120}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/hall', json=data, headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_hall_post2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/hall', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_hall_post3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'opacity': "erftgf"}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/hall', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'opacity': ['Not a valid integer.']}
    assert expected == json.loads(t1.get_data())


def test_hall_get1(client):
    res = flaskapp.test_client().get('/hall/456747')
    assert res.status_code == 404
    expected = {'message': 'Hall could not be found'}
    assert expected == json.loads(res.get_data())


def test_hall_get2(client):
    res = client.get('/hall/4')
    assert res.status_code == 200
    expected = b"Hall: opacity - 120"
    assert expected == res.get_data()


def test_hall_put1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'opacity': 447}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/hall/4457', json=data, headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Hall could not be found'}
    assert expected == json.loads(t1.get_data())


def test_hall_put2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/hall/2', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_hall_put3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'opacity': "ert"}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/hall/2', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'opacity': ['Not a valid integer.']}
    assert expected == json.loads(t1.get_data())


def test_hall_put4(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'opacity': 447}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/hall/2', json=data, headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_hall_delete1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().delete('/hall/4347', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Hall could not be found'}
    assert expected == json.loads(t1.get_data())


def test_hall_delete2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    if Hall.query.filter_by(id=1).first() is None:
        h1 = Hall(id=1, opacity=1414)
        db.session.add(h1)
        db.session.commit()
    t1 = flaskapp.test_client().delete('/hall/1', headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_admin_post1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'username': 'Teo', 'firstname': "T1", 'lastname': "R1",
            'email': "vedor@gmail.com", "password": "1111", "phone": "0987654321"}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/admin', json=data, headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_admin_post2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'username': 'Teo', 'firstname': "T1", 'lastname': 123,
            'email': "vedor@gmail.com", "password": "1111", "phone": "0987654321"}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/admin', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'lastname': ['Not a valid string.']}
    assert expected == json.loads(t1.get_data())


def test_admin_post3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/film', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_admin_get1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    res = flaskapp.test_client().get('/admin/45677', headers=headers)
    assert res.status_code == 404
    expected = {'message': 'Admin could not be found'}
    assert expected == json.loads(res.get_data())


def test_admin_get2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    res = flaskapp.test_client().get('/admin/5', headers=headers)
    assert res.status_code == 200
    expected = b"Admin: id - 5, username - abc, firstname - x, lastname - xx"
    assert expected == res.get_data()


def test_admin_put1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'username': "teodor"}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/admin/45677', json=data, headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Admin could not be found'}
    assert expected == json.loads(t1.get_data())


def test_admin_put2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/admin/2', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_admin_put3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'username': 125}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/admin/2', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'username': ['Not a valid string.']}
    assert expected == json.loads(t1.get_data())


def test_admin_delete1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().delete('/admin/478765', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Admin could not be found'}
    assert expected == json.loads(t1.get_data())


def test_admin_delete2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    if Admin.query.filter_by(id=43456).first() is None:
        a1 = Admin(id=43456, username='fff', firstname='er', lastname='erf', email='asd@gmail.com', password='1234',phone='09876543')
        db.session.add(a1)
        db.session.commit()
    t1 = flaskapp.test_client().delete('/admin/43456', headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_timetable_post1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'num_of_record': 2, 'film_id': 2, 'hall_id': 2}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/timetable', json=data, headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


def test_timetable_post2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'num_of_record': 2, 'film_id': "iuhyfdcvbn", 'hall_id': 2}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/timetable', json=data, headers=headers)
    assert t1.status_code == 422
    expected = {'film_id': ['Not a valid integer.']}
    assert expected == json.loads(t1.get_data())


def test_timetable_post3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().post('/timetable', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_timetable_get1(client):
    res = client.get('/timetable/4345677')
    assert res.status_code == 404
    expected = {'message': 'Timetable could not be found'}
    assert expected == json.loads(res.get_data())


def test_timetable_get2(client):
    res = client.get('/timetable/3')
    assert res.status_code == 200
    expected = b"Timetable id: 3, film-2, hall-2"
    assert expected == res.get_data()


def test_timetable_put1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'film_id': 23}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/timetable/44567', json=data, headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Timetable could not be found'}
    assert expected == json.loads(t1.get_data())


def test_timetable_put2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/timetable/2', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'No input data provided'}
    assert expected == json.loads(t1.get_data())


def test_timetable_put3(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    data = {'film_id': 1}
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().put('/timetable/2', json=data, headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Film could not be found'}
    assert expected == json.loads(t1.get_data())

def test_timetable_delete1(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    t1 = flaskapp.test_client().delete('/timetable/434567', headers=headers)
    assert t1.status_code == 404
    expected = {'message': 'Timetable could not be found'}
    assert expected == json.loads(t1.get_data())


def test_timetable_delete2(monkeypatch):
    monkeypatch.setattr(flask_jwt, '_jwt_required', fake_func)
    headers = {'x-access-token': token}
    if Timetable.query.filter_by(id=43456).first() is None:
        a1 = Timetable(id=43456, num_of_record=234, film_id=28, hall_id=53)
        db.session.add(a1)
        db.session.commit()
    t1 = flaskapp.test_client().delete('/timetable/43456', headers=headers)
    assert t1.status_code == 200
    expected = {'message': 'Success'}
    assert expected == json.loads(t1.get_data())


