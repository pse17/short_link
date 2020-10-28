import os
import re
import time
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate, validates, ValidationError
from hashids import Hashids

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
    long_url = db.Column(db.String(255), unique=True)
    postfix = db.Column(db.String(8), unique=True)
    count = db.Column(db.Integer, default=0)


# Shema
class LinkSchema(Schema):
    id = fields.Int()
    long_url = fields.Str()
    postfix = fields.Str(validate=validate.Length(max=8))
    count = fields.Int()
    short_link = fields.Method("make_short_link", dump_only=True)

    def make_short_link(self, link):
        return "http://mydomen.ru/{}".format(link.postfix)
    
    @validates("long_url")
    def validate_long_url(self, value):

        regex = ("((http|https)://)" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")
        s = re.compile(regex)
        if re.match(s, value) is None:
            raise ValidationError("URL is not valid")
 

# API
@app.route('/')
def help():
    message = r"Valid is: /long_to_short, /<short_postfix>, /statistics/<short_postfix>"
    return {"message": message}, 400


@app.route('/long_to_short/', methods=['POST'])
def long_to_short():
    json_data = request.get_json()
    if not json_data:
        return {"message": "No input data provided"}, 400
    
    try:
        # Validate URL
        schema = LinkSchema(only=('long_url',))
        data = schema.load(json_data)
    except ValidationError as message:
        return {"message": message}, 400

    code = 200
    link = Link.query.filter_by(long_url=data.long_url)
    if link is None:
        link = Link(long_url=data.long_url)
        link.postfix = get_postfix(link.id)
        db.session.commit()
        code = 201
    
    schema = LinkSchema(only=('short_link',))
    return schema.dump(link), code


@app.route('/<short_postfix>')
def redirect_to_long_link(short_postfix):
    if not validate_postfix(short_postfix):
        return {"message": "Postfix not valid"}, 400
    
    link = Link.query.filter_by(postfix=short_postfix)
    if link is None:
        return {"message": "Postfix not exist"}, 400
    
    # Increment counter
    link.count += 1
    # Redirect to previous long url
    return redirect(link.long_url, code=302)


@app.route('/statistics/<short_postfix>')
def statistics(short_postfix):
    if not validate_postfix(short_postfix):
        return {"message": "Postfix not valid"}, 400
    
    link = Link.query.filter_by(postfix=short_postfix)
    if link is None:
        return {"message": "Postfix not exist"}, 400

    schema = LinkSchema(only=('count',))
    return schema.dump(link), 200


def validate_postfix(postfix):
    try:
        schema = LinkSchema(only=('postfix',))
        schema.load(postfix)
    except ValidationError:
        return False
    return True


def get_postfix(id):
    hashids = Hashids(salt="salt is poison")
    postfix = hashids.encode(int(time.time()))
    return postfix