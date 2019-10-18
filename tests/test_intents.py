import pytest
from snipsroku.snipsroku import SnipsRoku
from snipsroku.clientMPU import ClientMPU
from hermes_demo_helper import *
from paho.mqtt.publish import single
import json
import random
import string
import urllib

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


def init_app(requests_mock):
    requests_mock.post('http://localhost:8060/keypress/Home', text='OK')
    roku_player = SnipsRoku(roku_device_ip="localhost")
    lang_config = Lang_config('ressources')
    return  ClientMPU("localhost:1883", lang_config, roku_player)

def test_intent_go_home(requests_mock):
    payload = create_intent("go_home_intent.json")
    client = init_app(requests_mock)
    with Hermes(client._ClientAction__mqtt_addr) as h:
        for i in client.intent_funcs:
            for name in client.config.intents.get_intent(i[1]):
                h.subscribe_intent(name, i[0])
        h.loop_start()
        single("hermes/intent/snips-demo:goHome", payload = payload)
        time.sleep(0.1)
        h.loop_stop()
    assert requests_mock.call_count == 2

def test_intent_launch_app(requests_mock):
    payload = create_intent("launch_netflix_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/launch/12'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post(post_addr, text='')
    client = init_app(requests_mock)
    with Hermes(client._ClientAction__mqtt_addr) as h:
        for i in client.intent_funcs:
            for name in client.config.intents.get_intent(i[1]):
                h.subscribe_intent(name, i[0])
        h.loop_start()
        single("hermes/intent/snips-demo:launchApp", payload = payload)
        time.sleep(0.5)
        h.loop_stop()
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.path in  post_addr

def test_intent_search_action_movies(requests_mock):
    query = {'type': 'movie','keyword':'action', 'launch': 'false'}
    payload = create_intent("search_action_movies_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post(post_addr, text='')
    client = init_app(requests_mock)
    with Hermes(client._ClientAction__mqtt_addr) as h:
        for i in client.intent_funcs:
            for name in client.config.intents.get_intent(i[1]):
                h.subscribe_intent(name, i[0])
        h.loop_start()
        single("hermes/intent/snips-demo:searchContent", payload = payload)
        time.sleep(0.5)
        h.loop_stop()
    assert requests_mock.last_request.path in  post_addr
    assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))

def test_intent_play_black_mirror_NetFlix_season1(requests_mock):
    query = {'keyword':'black mirror', 'launch': 'true', 'provider':'netflix', 'match-any':'true', 'season':'1'}
    payload = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post(post_addr, text='')
    client = init_app(requests_mock)
    with Hermes(client._ClientAction__mqtt_addr) as h:
        for i in client.intent_funcs:
            for name in client.config.intents.get_intent(i[1]):
                h.subscribe_intent(name, i[0])
        h.loop_start()
        single("hermes/intent/snips-demo:playContent", payload = payload)
        time.sleep(0.5)
        h.loop_stop()
    assert requests_mock.last_request.path in  post_addr
    assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))

def test_intent_play_then_pause(requests_mock):
    query = {'keyword':'black mirror', 'launch': 'true', 'provider':'netflix', 'match-any':'true', 'season':'1'}
    payload = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post('http://localhost:8060/keypress/Play', text='')
    requests_mock.post(post_addr, text='')
    client = init_app(requests_mock)
    with Hermes(client._ClientAction__mqtt_addr) as h:
        for i in client.intent_funcs:
            for name in client.config.intents.get_intent(i[1]):
                h.subscribe_intent(name, i[0])
        h.loop_start()
        single("hermes/intent/snips-demo:playContent", payload = payload)
        time.sleep(0.5)
        assert requests_mock.last_request.path in  post_addr
        assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))
        payload = create_intent("tv_pause_intent.json")
        single("hermes/intent/snips-demo:tvPause", payload = payload)
        time.sleep(0.5)
        assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'
        h.loop_stop()

def test_intent_play_then_pause_then_play(requests_mock):
    query = {'keyword':'black mirror', 'launch': 'true', 'provider':'netflix', 'match-any':'true', 'season':'1'}
    payload = create_intent("play_black_mirror_Netflix_season1_intent.json")
    response = load_query_response('query_apps.xml')
    post_addr ='http://localhost:8060/search/browse'
    requests_mock.get('http://localhost:8060/query/apps', text=response)
    requests_mock.post('http://localhost:8060/keypress/Play', text='')
    requests_mock.post(post_addr, text='')
    client = init_app(requests_mock)
    with Hermes(client._ClientAction__mqtt_addr) as h:
        for i in client.intent_funcs:
            for name in client.config.intents.get_intent(i[1]):
                h.subscribe_intent(name, i[0])
        h.loop_start()
        single("hermes/intent/snips-demo:playContent", payload = payload)
        time.sleep(0.5)
        assert requests_mock.last_request.path in  post_addr
        assert query == dict(urllib.parse.parse_qsl(requests_mock.last_request.query))
        payload = create_intent("tv_pause_intent.json")
        single("hermes/intent/snips-demo:tvPause", payload = payload)
        time.sleep(0.5)
        nb_called = requests_mock.call_count
        assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'
        payload = create_intent("tv_play_intent.json")
        single("hermes/intent/snips-demo:tvPlay", payload = payload)
        time.sleep(0.5)
        assert nb_called + 1 == requests_mock.call_count
        assert requests_mock.last_request.path in  'http://localhost:8086/keypress/play'
        h.loop_stop()
