# My_project
## Instalation

Use the package manager pip to install pyenv.
```bash
pip install pyenv
```

Use the package manager pyenv to install python.
```bash
pyenv install 3.8.3
```

Use the package manager pip to install pipenv.
```bash
pip install --user pipenv
```
Use the package manager pip to install flask.
```bash
pip install flask
```
## Gunicorn
Install gunicorn in pipenv
```bash
pipenv install gunicorn
```
## Usage
```bash
from flask import Flask

app = Flask(__name__)


@app.route('/api/v1/hello-world-<int:variant>')
def hello_world(variant):
    return 'Hello World ' + str(variant)


@app.route('/')
def main_page():
    return 'My Project'


if __name__ == '__main__':
    app.run()
```
## Running with gunicorn
``` bash
pipenv run gunicorn -w 4 app:app
```
## License
[MIT](https://choosealicense.com/licenses/mit/)
