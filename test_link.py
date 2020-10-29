import pytest
import json
from short_link.short_link import LinkSchema

'''
def test_client_root(test_client):
    response = test_client.get('/')
    assert response.status_code == 400
    assert b"Valid is:" in response.data 

def test_client_long_to_short(test_client):
    response = test_client.post('/long_to_short/',
        data = json.dumps(dict(long_url='http://ya.ru')),
        content_type='application/json')
    data = json.loads(response.data.decode())
    assert response.status_code == 201
    assert "http://mydomen.ru/" in data['short_link']
'''

def test_model_link(get_db, get_link):
    link = get_link
    assert link.long_url == 'http://ya.ru'
    assert link.count == 0
    assert link.id == 1 

def test_link_shema_dump(get_db, get_link):
    link = get_link
    schema = LinkSchema()    
    dump = schema.dump(link)
    assert dump['id'] == 1
    assert dump["long_url"] == 'http://ya.ru'
    assert dump["count"] == 0
    assert "http://mydomen.ru/" in dump["short_link"] 

