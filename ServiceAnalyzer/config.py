import configparser

CONFIG_PATH = './config.ini'

config = None


def get_config():
    global config
    if config:
        return config
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config
