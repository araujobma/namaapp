from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']


@app.route('/')
def hello_world():
    return render_template("home.html")


if __name__ == '__main__':
    app.run()
