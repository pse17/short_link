import pytest
import json
from short_link.short_link import LinkSchema, Link
from marshmallow import ValidationError


def test_model_link(get_db, get_link):
    link = get_link
    assert link.long_url == 'http://ya.ru'
    assert link.count == 0
    assert link.id == 1 


def test_link_shema_dump(get_db, get_link):
    link = get_link
    dump = LinkSchema().dump(link)
    assert dump['id'] == 1
    assert dump["long_url"] == 'http://ya.ru'
    assert dump["count"] == 0
    assert "http://mydomen.ru/" in dump['short_url']


def test_link_schema_load(get_db, get_link):
    with pytest.raises(ValidationError):
        LinkSchema(only=('long_url',)).load({'long_url': 'foo'})

    data = LinkSchema(only=('long_url',)).load({'long_url': 'http://ya.ru'})
    assert data.long_url  == 'http://ya.ru'


def test_client_long_to_short(get_client, get_db):
    test_client = get_client
    
    # Add new link
    response = test_client.post(
        '/long_to_short/',
        json = {'long_url': 'http://google.com'})
    data = json.loads(response.data)
    assert "http://mydomen.ru/" in data['short_url']
    assert response.status_code == 201
    
    # Get exist link
    response = test_client.post(
        '/long_to_short/',
        json = {'long_url': 'http://google.com'})
    assert response.status_code == 200

    # Get bad request, url is not valid
    response = test_client.post(
        '/long_to_short/',
        json = {'long_url': 'foo'})
    data = json.loads(response.data)
    assert response.status_code == 400
    assert "URL is not valid" in data['message']


def test_client_short_postfix(get_client, get_db):
    test_client = get_client
    db = get_db
    
    short_postfix = 'qwertyu'
    link = Link(postfix=short_postfix)
    db.session.add(link)
    db.session.commit()
    
    response = test_client.get("/%s" % short_postfix)
    assert response.status_code == 302
    assert 

    bad_postfix = "1234567890"
    response = test_client.get("/%s" % bad_postfix)
    data = json.loads(response.data)
    assert response.status_code == 400
    assert "Postfix not exist" in data['message']






