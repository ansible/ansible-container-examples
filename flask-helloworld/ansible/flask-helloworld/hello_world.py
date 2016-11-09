from flask import Flask, render_template

APP = Flask(__name__)

@APP.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0')
