import pytest
from short_link.short_link import app, db, Link

@pytest.fixture(scope="module")
def get_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope="module")
def get_db():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield db
    
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope="function")
def get_link(get_db):
    postfix = 'qwertyu'
    link = Link(long_url='http://ya.ru', postfix=postfix) 
    db = get_db
    db.session.add(link)
    db.session.commit()
    yield link
    db.session.delete(link)
    db.session.commit()
