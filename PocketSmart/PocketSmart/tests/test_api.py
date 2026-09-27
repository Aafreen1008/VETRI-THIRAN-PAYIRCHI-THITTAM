import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ["DATABASE_URL"]="sqlite:///./data/test_pocketsmart.db"
os.environ["SECRET_KEY"]="test-secret"
from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    r=client.get('/api/health')
    assert r.status_code==200
    assert r.json()['status']=='ok'

def test_register_login_and_plan():
    username='testuser_api'
    client.post('/api/auth/register',json={'username':username,'email':username+'@example.com','full_name':'Test User','password':'password123'})
    r=client.post('/api/auth/login',json={'username':username,'password':'password123'})
    assert r.status_code==200
    token=r.json()['access_token']
    h={'Authorization':'Bearer '+token}
    r=client.post('/api/planner/home',headers=h,json={'total_budget':30000,'num_lights':2,'num_fans':2,'num_furniture':1,'num_dining_tables':1,'has_living_room':True,'has_kitchen':False,'has_bedroom':True,'additional_requirements':''})
    assert r.status_code==200
    assert r.json()['remaining_budget']>=0
