import pytest
from snipsroku.snipsroku import SnipsRoku
from snipsroku.clientMPU import ClientMPU
from hermes_demo_helper import *
from paho.mqtt.publish import single
import json
import random
import string
import urllib
import subprocess
import socket
import paho.mqtt.client as mqtt
import os

@pytest.fixture(scope="module")
def mqtt_server():
    os.environ["PATH"] += os.pathsep + os.pathsep.join(["/usr/sbin", "/usr/local/sbin"])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 0))
    port = s.getsockname()[1]
    s.close()
    print("Starting MQTT Server")
    mqtt_server = subprocess.Popen(["mosquitto", "-v", "-p", "{}".format(port)])
    time.sleep(4)  # Let's wait a bit before it's started
    client = mqtt.Client()
    while client.connect("0.0.0.0", port, 60):
        time.sleep(0.5)
        pass
    yield (port, mqtt_server)
    print("Tearing down MQTT Server")
    mqtt_server.kill()


def create_session_id(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def create_intent(filename, site_id = 'default',session_id = None):
    if session_id is None:
        session_id = create_session_id()
    with open('tests/payloads/' + filename, 'r') as f:
        data = json.load(f)
        data['siteId'] = site_id
        data['sessionId'] = session_id
        return json.dumps(data)
    return '{}'

def load_query_response(filename):
    with open('tests/responses/' + filename, 'r') as f:
        return f.read()
    return ''


class init_app:
    def __init__(self, requests_mock, port):
        requests_mock.post('http://localhost:8060/keypress/Home', text='OK')
        lang_config = Lang_config('ressources')
        roku_player = SnipsRoku(roku_device_ip="localhost")
        self.client = ClientMPU("0.0.0.0:{}".format(port[0]), lang_config, roku_player)

    def __enter__(self):
        print("mqtt addr")
        print(self.client._ClientAction__mqtt_addr)
        self.h = Hermes(self.client._ClientAction__mqtt_addr)
        self.h.connect()
        for i in self.client.intent_funcs:
            for name in self.client.config.intents.get_intent(i[1]):
                self.h.subscribe_intent(name, i[0])
        self.h.loop_start()
        time.sleep(0.1)
        return self.client
    
    def __exit__(self, exception_type, exception_val, trace):
        time.sleep(0.5)
        if not exception_type:
            return self.h.disconnect()
        return False

def test_intent_go_home(requests_mock, mqtt_server):
    payload = create_intent("go_home_intent.json")
    with init_app(requests_mock, mqtt_server) as client:
        single("hermes/intent/snips-demo:goHome", payload = payload, port=mqtt_server[0])
        time.sleep(0.1)
    assert requests_mock.call_count == 2

def test_intent_launch_app(requests_mock, mqtt_server):
    payload = create_intent("launch_netflix_intent.json")
    post_addr ='http://localhost:8060/launch/12'
    requests_mock.get('http://localhost:8060/query/apps', text = load_query_response('query_apps.xml'))
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server) as client:
        single("hermes/intent/snips-demo:launchApp", payload = payload, port=mqtt_server[0])
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.path in  post_addr

def test_intent_search_action_movies(requests_mock, mqtt_server):
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.post(post_addr, text='')
    requests_mock.get('http://localhost:8060/query/apps', text=load_query_response('query_apps.xml'))
    with init_app(requests_mock, mqtt_server) as client:
        payload = create_intent("search_action_movies_intent.json")
        single("hermes/intent/snips-demo:searchContent", payload = payload, port=mqtt_server[0])
    assert requests_mock.last_request.path in  post_addr
    query = {'type': 'movie','keyword':'action', 'launch': 'false'}
    assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))

def test_intent_play_black_mirror_NetFlix_season1(requests_mock, mqtt_server):
    query = {'keyword':'black mirror', 'launch': 'true', 'provider':'netflix', 'match-any':'true', 'season':'1'}
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server) as client:
        payload = create_intent("play_black_mirror_Netflix_season1_intent.json")
        single("hermes/intent/snips-demo:playContent", payload = payload, port=mqtt_server[0])
    assert requests_mock.last_request.path in  post_addr
    assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))

def test_intent_play_then_pause(requests_mock, mqtt_server):
    query = {'keyword':'black mirror', 'launch': 'true', 'provider':'netflix', 'match-any':'true', 'season':'1'}
    payload = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post('http://localhost:8060/keypress/Play', text='')
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server) as client:
        single("hermes/intent/snips-demo:playContent", payload = payload, port=mqtt_server[0])
        time.sleep(0.5)
        assert requests_mock.last_request.path in  post_addr
        assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))
        payload = create_intent("tv_pause_intent.json")
        single("hermes/intent/snips-demo:tvPause", payload = payload, port=mqtt_server[0])
    assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'

def test_intent_play_then_pause_then_play(requests_mock, mqtt_server):
    query = {'keyword':'black mirror', 'launch': 'true', 'provider':'netflix', 'match-any':'true', 'season':'1'}
    payload = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post('http://localhost:8060/keypress/Play', text='')
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server) as client:
        single("hermes/intent/snips-demo:playContent", payload = payload, port=mqtt_server[0])
        time.sleep(0.5)
        assert requests_mock.last_request.path in  post_addr
        assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))
        payload = create_intent("tv_pause_intent.json")
        single("hermes/intent/snips-demo:tvPause", payload = payload, port=mqtt_server[0])
        time.sleep(0.5)
        nb_called = requests_mock.call_count
        assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'
        payload = create_intent("tv_play_intent.json")
        single("hermes/intent/snips-demo:tvPlay", payload = payload, port=mqtt_server[0])
    assert nb_called + 1 == requests_mock.call_count
    assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'
