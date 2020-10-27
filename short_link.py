from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import os

app = Flask(__name__)


# Config 
env = os.environ.get('FLASK_ENV')
if env == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Model
db = SQLAlchemy(app)
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(255), unique=True, nullable=False)
    suffix = db.Column(db.String(6), unique=True, nullable=False)
    count = db.Column(db.Integer)


# Shema
class LinkSchema(Schema):
    id = fields.Int()
    long_url = fields.Str()
    suffix = fields.Str()
    count = fields.Int()
    short_link = fields.Method("make_short_link", dump_only=True)

    def make_short_link(self, link):
        return "http://mydomen.ru/{}".format(link.suffix)

only_link_schema = LinkSchema(only=('long_url',))
only_count_schema = LinkSchema(only=('count',))
only_short_link_schema = LinkSchema(only=('short_link',))


# API
@app.route('/')
def help():
    message = r'''Valid is: /long_to_short - get shortlink, /<short_postfix> - redirect to link whth this postfix,
         /statistics/<short_postfix> -the number of clicks on short link whth this postfix'''
    return {"message": message}, 400


@app.route('/long_to_short')
def long_to_short():
    return {}


@app.route('/<short_postfix>')
def redirect_to_long_link(short_postfix):
    return {}


@app.route('/statistics/<short_postfix>')
def statistics(short_postfix):
    return {}