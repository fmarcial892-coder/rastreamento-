import os
import tempfile

fd, path = tempfile.mkstemp(); os.close(fd)
os.environ['DB_PATH'] = path
os.environ['ADMIN_USER'] = 'pitbull'
os.environ['ADMIN_PASSWORD'] = '1533'
from app import app

with app.test_client() as client:
    assert client.get('/').status_code == 200
    response = client.post('/api/orders', json={'street':'Rua Teste','number':'10','complement':'','neighborhood':'Centro','city':'Valinhos','state':'SP','cep':'13279-813'})
    assert response.status_code == 201, response.get_data(as_text=True)
    code = response.json['tracking_code']
    assert client.get('/api/orders/'+code).status_code == 200
    assert client.get('/admin').status_code == 302
    login = client.post('/admin/login', data={'username':'pitbull','password':'1533'})
    assert login.status_code == 302
    assert client.get('/admin').status_code == 200
    assert client.post('/api/admin/orders/1/status', json={'status':'released'}).status_code == 200
    order = client.get('/api/orders/'+code).json
    assert order['status'] == 'released'
print('public=OK login=OK order=OK status-update=OK')
