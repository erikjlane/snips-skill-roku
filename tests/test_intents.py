import json
import os
import random
import socket
import string
import subprocess
import time
import urllib

import paho.mqtt.client as mqtt
import pytest
from hermes_python.hermes import Hermes
from paho.mqtt.publish import single

from hermes_demo_helper.lang_config import Lang_config
from hermes_demo_helper.hermes_demo_helper import SnipsFlow
from snipsroku.snipsroku import SnipsRoku
from snipsroku.clientMPU import flow


@pytest.fixture(scope="module")
def mqtt_server():
    os.environ["PATH"] += os.pathsep + os.pathsep.join(["/usr/sbin", "/usr/local/sbin"])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    print("Starting MQTT Server")
    mqtt_server = subprocess.Popen(["mosquitto", "-v", "-p", "{}".format(port)])
    time.sleep(2)  # Let's wait a bit before it's started
    client = mqtt.Client()
    while client.connect("127.0.0.1", port, 60):
        time.sleep(1)
    lang_config = Lang_config('resources')
    flow.set_lang_config(lang_config)
    yield (port, mqtt_server)
    print("Tearing down MQTT Server")
    mqtt_server.kill()


def create_session_id(string_length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


def create_intent(filename, site_id='default', session_id=None):
    if session_id is None:
        session_id = create_session_id()
    with open('tests/payloads/' + filename, 'r') as f:
        data = json.load(f)
        data['siteId'] = site_id
        data['sessionId'] = session_id
        return (json.dumps(data), site_id, session_id)
    return ('{}', site_id, session_id)


def load_query_response(filename):
    with open('tests/responses/' + filename, 'r') as f:
        return f.read()
    return ''


class init_app:
    def __init__(self, requests_mock, port):
        requests_mock.post('http://localhost:8060/keypress/Home', text='OK')
        roku_player = SnipsRoku(roku_device_ip="localhost")
        flow.set_host("127.0.0.1:{}".format(port[0]))
        flow.set_data(roku_player=roku_player)
        flow.start(loop=False)
        time.sleep(1)
        self.flow = flow

    def __enter__(self):
        time.sleep(1)
        return self.flow
    
    def __exit__(self, exception_type, exception_val, trace):
        time.sleep(1)
        if not exception_type:
            return self.flow.stop()
        return False


def test_intent_go_home(requests_mock, mqtt_server):
    payload, _, _ = create_intent("go_home_intent.json")
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:goHome",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.1)
    assert requests_mock.call_count == 2

def test_intent_tv_forward(requests_mock, mqtt_server):
    payload, _, _ = create_intent("tv_forward_intent.json")
    requests_mock.post("http://localhost:8060/keypress/Fwd", text="OK")
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:tvForward",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.1)
        assert requests_mock.call_count == 2
        requests_mock.post('http://localhost:8060/keypress/play', text='')
        # TODO add not recognized
        time.sleep(15)
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.path in 'http://localhost:8060/keypress/play'

def test_intent_tv_forward_play(requests_mock, mqtt_server):
    payload, site_id, session_id = create_intent("tv_forward_intent.json")
    requests_mock.post("http://localhost:8060/keypress/Fwd", text="OK")
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:tvForward",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.1)
        assert requests_mock.call_count == 2
        requests_mock.post('http://localhost:8060/keypress/play', text='')
        payload, site_id, session_id = create_intent("tv_play_intent.json", site_id, session_id)
        single("hermes/intent/snips-demo:tvResume",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.1)
        payload, site_id, session_id = create_intent("end_session_nominal.json", site_id, session_id)
        single("hermes/dialogueManager/sessionEnded",
               payload=payload,
               port=mqtt_server[0])
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.path in 'http://localhost:8060/keypress/play'

def test_intent_tv_forward_play_wait(requests_mock, mqtt_server):
    payload, site_id, session_id = create_intent("tv_forward_intent.json")
    requests_mock.post("http://localhost:8060/keypress/Fwd", text="OK")
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:tvForward",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.1)
        assert requests_mock.call_count == 2
        requests_mock.post('http://localhost:8060/keypress/play', text='')
        payload, site_id, session_id = create_intent("tv_play_intent.json", site_id, session_id)
        single("hermes/intent/snips-demo:tvResume",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.1)
        payload, site_id, session_id = create_intent("end_session_nominal.json", site_id, session_id)
        single("hermes/dialogueManager/sessionEnded",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(15)
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.path in 'http://localhost:8060/keypress/play'

def test_intent_launch_app(requests_mock, mqtt_server):
    payload, _, _ = create_intent("launch_netflix_intent.json")
    post_addr = 'http://localhost:8060/launch/12'
    requests_mock.get('http://localhost:8060/query/apps',
                      text=load_query_response('query_apps.xml'))
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:launchApp",
               payload=payload,
               port=mqtt_server[0])
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.path in post_addr


def test_intent_search_action_movies(requests_mock, mqtt_server):
    post_addr = 'http://localhost:8060/search/browse'
    requests_mock.post(post_addr, text='')
    requests_mock.get('http://localhost:8060/query/apps',
                      text=load_query_response('query_apps.xml'))
    with init_app(requests_mock, mqtt_server):
        payload, _, _ = create_intent("search_action_movies_intent.json")
        single("hermes/intent/snips-demo:searchContent",
               payload=payload,
               port=mqtt_server[0])
    assert requests_mock.last_request.path in  post_addr
    query = {
        'type': 'movie',
        'keyword': 'action',
        'launch': 'false'
    }
    assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))


def test_intent_play_black_mirror_netflix_season1(requests_mock, mqtt_server):
    query = {
        'keyword': 'black mirror',
        'launch': 'true',
        'provider': 'netflix',
        'match-any': 'true',
        'season': '1'
    }
    response = load_query_response('query_apps.xml')
    post_addr = 'http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server):
        payload, _, _ = create_intent("play_black_mirror_Netflix_season1_intent.json")
        single("hermes/intent/snips-demo:playContent", payload = payload, port=mqtt_server[0])
    assert requests_mock.last_request.path in post_addr
    assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))


def test_intent_play_then_pause(requests_mock, mqtt_server):
    query = {
        'keyword': 'black mirror',
        'launch': 'true',
        'provider': 'netflix',
        'match-any': 'true',
        'season': '1'
    }
    payload, _, _ = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr = 'http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post('http://localhost:8060/keypress/Play', text='')
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:playContent", payload=payload, port=mqtt_server[0])
        time.sleep(0.5)
        assert requests_mock.last_request.path in post_addr
        assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))
        payload, _, _ = create_intent("tv_pause_intent.json")
        single("hermes/intent/snips-demo:tvPause", payload=payload, port=mqtt_server[0])
    assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'


def test_intent_play_then_pause_then_play(requests_mock, mqtt_server):
    query = {
        'keyword': 'black mirror',
        'launch': 'true',
        'provider': 'netflix',
        'match-any': 'true',
        'season': '1'
    }
    payload, _, _ = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr = 'http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post('http://localhost:8060/keypress/Play', text='')
    requests_mock.post(post_addr, text='')
    with init_app(requests_mock, mqtt_server):
        single("hermes/intent/snips-demo:playContent",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.5)
        assert requests_mock.last_request.path in post_addr
        assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))
        payload, _, _ = create_intent("tv_pause_intent.json")
        single("hermes/intent/snips-demo:tvPause",
               payload=payload,
               port=mqtt_server[0])
        time.sleep(0.5)
        nb_called = requests_mock.call_count
        assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'
        payload, _, _ = create_intent("tv_play_intent.json")
        single("hermes/intent/snips-demo:tvResume",
               payload=payload,
               port=mqtt_server[0])
    assert nb_called + 1 == requests_mock.call_count
    assert requests_mock.last_request.path in 'http://localhost:8086/keypress/play'
