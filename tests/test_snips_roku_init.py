import pytest
import mock
import roku
from snipsroku.snipsroku import SnipsRoku

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
