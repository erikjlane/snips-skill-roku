from .snipsTools import SnipsConfigParser

class Snips_config:
    @staticmethod
    def get_assistant_path(path="/etc/snips.toml"):
        snips_config = SnipsConfigParser.read_configuration_file(path)
        if snips_config is None:
            return '/var/lib/snips/assistant/assistant.json'
        config = snips_config.get('snips-common')
        if config is None:
            return '/var/lib/snips/assistant/assistant.json'
        
        return config.get('assistant', '/var/lib/snips/assistant') + '/assistant.json'
    @staticmethod
    def get_default_enable_feedback(path="/etc/snips.toml"):
        snips_config = SnipsConfigParser.read_configuration_file(path).get('snips-dialogue')
        if snips_config is None:
            return '/var/lib/snips/assistant/assistant.json'
        config = snips_config.get('snips-dialogue')
        if config is None:
            return '/var/lib/snips/assistant/assistant.json'
        return not config.get('sound_feedback_disabled_default', False)