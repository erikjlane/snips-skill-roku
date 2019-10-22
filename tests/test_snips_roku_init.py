import subprocess
import time

import mock
import pytest

from snipsroku.snipsroku import SnipsRoku


@pytest.fixture(scope="module")
def mqtt_server():
    print("Starting MQTT Server")
    mqtt_server = subprocess.Popen("mosquitto")
    time.sleep(1)  # Let's wait a bit before it's started
    yield mqtt_server
    print("Tearing down MQTT Server")
    mqtt_server.kill()


def test_no_roku_connected_without_ip():
    with mock.patch('roku.Roku.discover', return_value=None):
        with pytest.raises(Exception):
            SnipsRoku(roku_device_ip=None)


def test_no_roku_connected_with_ip():
    with pytest.raises(Exception):
        SnipsRoku(roku_device_ip="localhost")


def test_roku_connected_without_ip(requests_mock):
    class FakeRoku:
        def __init__(self):
            self.host = 'localhost'

        def home(self):
            pass

    with mock.patch('roku.Roku.discover', return_value=[FakeRoku()]):
        SnipsRoku(roku_device_ip=None)


def test_roku_connected_with_ip(requests_mock):
    requests_mock.post('http://localhost:8060/keypress/Home', text='OK')
    SnipsRoku(roku_device_ip="localhost")
