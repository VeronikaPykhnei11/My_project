from flask import Flask
app = Flask(__name__)

@app.route('/api/v1/hello-world-<int:variant>')
def hello_world(variant):
    return 'Hello World ' + str(variant) + "!"


@app.route('/')
def main_page():
    return 'My Project'


if __name__ == '__main__':
    app.run()
