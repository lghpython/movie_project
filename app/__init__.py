# coding: utf-8
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from flask_redis import FlaskRedis
import pymysql
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:lgh1991go@127.0.0.1:3306/movie"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "6e24e3c19b4d407d9ce668009066df1c"
app.config['REDIS_URL'] = "redis://:123456@192.168.0.5:6379/0"
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config['USER_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/user/")
app.debug = False
db = SQLAlchemy(app)
rd = FlaskRedis(app)

from app.admin import admin as admin_blueprint
from app.home import home as home_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')


@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"), 404
