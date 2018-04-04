from unittest import TestCase
import mock

from snipsroku.snipsroku import SnipsRoku


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class TestSkill(TestCase):

    def setUp(self):
        self.ip = "some_ip"
        self.roku = SnipsRoku(self.ip)
        self.available_apps = """<?xml version="1.0" encoding="UTF-8" ?>
        <apps>
            <app id="31863" type="menu" version="1.3.5">Roku Home News</app>
            <app id="12" subtype="ndka" type="appl" version="4.2.90418002">Netflix</app>
            <app id="13" subtype="ndka" type="appl" version="7.1.2017082110">Amazon Video</app>
        </apps>
        """
        self.apps_string_list = 'Roku Home News,Netflix,Amazon Video'

    def get_search_payload(self, content_type, keyword=None, title=None, launch=False, provider=None,
                           season=None):
        payload = {'type': content_type, 'launch': SnipsRoku.bool2string(launch),
                   'season': season}
        if launch:
            payload['match-any'] = 'true'
            if provider is None:
                payload['provider'] = self.apps_string_list
            else:
                payload['provider'] = provider

        if title is not None:
            payload['title'] = title
        elif keyword is not None:
            payload['keyword'] = keyword
        return payload

    @mock.patch('snipsroku.snipsroku.requests')
    def test_set_available_apps(self, mock_request):
        r = AttrDict()
        r.update({'content': self.available_apps})
        mock_request.get.return_value = r
        self.roku.set_available_apps()

    @mock.patch('snipsroku.snipsroku.requests')
    def test_launch_app(self, mock_request):
        app_id = 12
        self.roku.launch_app(app_id)
        mock_request.post.assert_called_with("http://{}:8060/launch/{}".format(self.ip, app_id))

    @mock.patch('snipsroku.snipsroku.requests')
    def test_get_app_id(self, mock_request):
        r = AttrDict()
        r.update({'content': self.available_apps})
        mock_request.get.return_value = r
        assert self.roku.get_app_id('netflix'), 12
        self.assertTrue(mock_request.get.called)

    @mock.patch('snipsroku.snipsroku.requests')
    def test_search_content(self, mock_request):
        r = AttrDict()
        r.update({'content': self.available_apps})
        mock_request.get.return_value = r
        self.roku.set_available_apps()
        content_type = 'tv-show'
        launch = False
        season = 3
        title = 'Black Mirror'
        payload = self.get_search_payload(content_type, None, title, launch, None, season)
        self.roku.search_content(content_type, None, title, launch, None, season)
        mock_request.post.assert_called_with("http://{}:8060/search/browse?".format(self.ip), params=payload)

    @mock.patch('snipsroku.snipsroku.requests')
    def test_search_content_launch(self, mock_request):
        r = AttrDict()
        r.update({'content': self.available_apps})
        mock_request.get.return_value = r
        self.roku.set_available_apps()
        content_type = 'tv-show'
        launch = True
        season = 3
        title = 'Black Mirror'
        payload = self.get_search_payload(content_type, None, title, launch, None, season)
        self.roku.search_content(content_type, None, title, launch, None, season)
        mock_request.post.assert_called_with("http://{}:8060/search/browse?".format(self.ip), params=payload)

    @mock.patch('snipsroku.snipsroku.requests')
    def test_search_content_error(self, mock_request):
        r = AttrDict()
        r.update({'content': self.available_apps})
        mock_request.get.return_value = r
        self.roku.set_available_apps()
        content_type = 'tv-show'
        launch = False
        season = 3
        title = 'Black Mirror'
        try:
            self.roku.search_content(content_type, None, title, launch, None, season)
        except ValueError as e:
            assert e.message, 'Either keyword or title need to be specified'

    @mock.patch('snipsroku.snipsroku.requests')
    def test_play(self, mock_request):
        self.roku.play()
        mock_request.post.assert_called_with("http://{}:8060/keypress/Play".format(self.ip))

    @mock.patch('snipsroku.snipsroku.requests')
    def test_home_screen(self, mock_request):
        self.roku.home_screen()
        mock_request.post.assert_called_with("http://{}:8060/keypress/Home".format(self.ip))

    def test_no_ip_on_instantiation(self):
        try:
            SnipsRoku()
        except ValueError as e:
            assert e.message, 'You need to provide a Roku device IP'
