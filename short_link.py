from flask import Flask
import hashids

app = Flask(__name__)

@app.route('/')
def help():
    return '/long_to_short - get shortlink, /\<short-link\> - redirect to this link,\
         /statistics/<short-link> -the number of clicks on this short link'


@app.route('/long_to_short')
def long_to_short():
    pass


@app.route('/statistics/<short_postfix>')
def redirect_to_long_link(short_postfix):
    pass


@app.route('/statistics/<short_postfix>')
def statistics(short_postfix):
    pass





'''
hashids = hashids.Hashids(
    salt="Salt is white poison", 
    min_length=6,
    alphabet='abcdefghijklmnopqrstuvwxyz1234567890')

hash_pk = hashids.encode(223)
print(hash_pk)
pk = hashids.decode(hash_pk)
print(pk)
'''
