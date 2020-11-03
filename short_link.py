import os
import re
import time
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from hashids import Hashids


app = Flask(__name__)

# Config 
env = os.environ.get('FLASK_ENV')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if env == 'development':
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///links.db'


# Model
db = SQLAlchemy(app)

class Link(db.Model):
    """ Describe model link"""
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(255), unique=True)
    postfix = db.Column(db.String(8), unique=True)
    count = db.Column(db.Integer, default=0)


# Shema
class LinkSchema(Schema):
    id = fields.Int()
    long_url = fields.Str()
    postfix = fields.Str()
    count = fields.Int()
    short_url = fields.Function(lambda obj: "http://mydomen.ru/{}".format(obj.postfix))

    @post_load
    def make_link(self, data, **kwargs):
        return Link(**data)
    
    @validates('long_url')
    def validate_long_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex, url) is None:
            raise ValidationError("URL is not valid")
 

# API
@app.route('/')
def root():
    message = r"Valid is: /long_to_short, /<short_postfix>, /statistics/<short_postfix>"
    return {"message": message}, 400


@app.route('/long_to_short/', methods=['POST'])
def long_to_short():
    if request.method == 'POST':
        data = request.get_json()

    if not data:
        return {"message": "No input data provided"}, 400
    
    try:
        # Validate URL
        load_data = LinkSchema(only=('long_url',)).load(data)
    except ValidationError:
        return {"message": "URL is not valid"}, 400

    #If exists
    code = 200
    link = Link.query.filter_by(long_url=load_data.long_url).first()
    
    if link is None:
        link = load_data
        link.postfix = get_postfix()
        db.session.add(link)
        db.session.commit()
        code = 201

    return LinkSchema(only=('short_url',)).dumps(link), code


@app.route('/<short_postfix>')
def redirect_to_long_link(short_postfix):
    link = Link.query.filter_by(postfix=short_postfix).first()
    if link is None:
        return {"message": "Postfix not exist"}, 400
    
    # Increment counter
    link.count = link.count + 1
    db.session.commit()
    # Redirect to previous long url
    return redirect(link.long_url, code=302)


@app.route('/statistics/<short_postfix>')
def statistics(short_postfix):
   
    link = Link.query.filter_by(postfix=short_postfix).first()
    if link is None:
        return {"message": "Postfix not exist"}, 400

    return LinkSchema(only=('count',)).dumps(link), 200


def get_postfix():
    hashids = Hashids(salt="salt is poison")
    postfix = hashids.encode(int(time.time()))
    return postfix