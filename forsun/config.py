# -*- coding: utf-8 -*-
# 15/6/27
# create by: snower

import os
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import configparser
from .utils import string_type, number_type

class ConfFileNotFoundError(Exception):
    pass

__config = {}

DEFAULT_CONFIG = {
    "LOG_FILE": "/var/log/funsun.log",
    "LOG_LEVEL": "ERROR",
    "LOG_FORMAT": "",

    "BIND_ADDRESS": "0.0.0.0",
    "PORT": 6458,

    "HTTP_BIND": "",

    "STORE_DRIVER": "mem",

    "STORE_MEM_STORE_FILE": "/tmp/forsun.session",

    "STORE_REDIS_HOST": "127.0.0.1",
    "STORE_REDIS_PORT": 6379,
    "STORE_REDIS_DB": 0,
    "STORE_REDIS_PREFIX": "forsun",
    "STORE_REDIS_SERVER_ID": 0,
    "STORE_REDIS_MAX_CONNECTIONS": 8,
    "STORE_REDIS_CLIENT_TIMEOUT": 7200,
    "STORE_REDIS_BULK_SIZE": 5,
    "STORE_REDIS_CURRENTTIME_EXPRIED": 2592000,
    "STORE_REDIS_PLAN_EXPRIED": 604800,
    "STORE_REDIS_PLANTIME_EXPRIED": 604800,

    "ACTION_RETRY_DELAY_SECONDS": 3,
    "ACTION_RETRY_DELAY_RATE": 1,
    "ACTION_RETRY_MAX_COUNT": 3,
    "ACTION_POLL_IDLE_SECONDS": 120,
    "ACTION_SHELL_CWD": "/tmp",
    "ACTION_HTTP_MAX_CLIENTS": 64,
    "ACTION_HTTP_CONNECT_TIMEOUT": 5,
    "ACTION_HTTP_REQUEST_TIMEOUT": 120,
    "ACTION_HTTP_USER_AGENT": "",
    "ACTION_REDIS_MAX_CONNECTIONS": 8,
    "ACTION_REDIS_CLIENT_TIMEOUT": 7200,
    "ACTION_REDIS_BULK_SIZE": 5,
    "ACTION_THRIFT_MAX_CONNECTIONS": 64,
    "ACTION_MYSQL_USER": "root",
    "ACTION_MYSQL_PASSWD": "",
    "ACTION_MYSQL_MAX_CONNECTIONS": 8,
    "ACTION_MYSQL_WAIT_CONNECTION_TIMEOUT": 7200,
    "ACTION_MYSQL_IDLE_SECONDS": 120,

    "EXTENSION_PATH": "",
    "EXTENSIONS": [],
}

def get(name, default=None):
    return __config.get(name, default)

def set(name, value):
    old_value = __config[name]
    __config[name] = value
    return old_value

def update(config):
    __config.update(config)
    return __config

update(DEFAULT_CONFIG)
for key, value in DEFAULT_CONFIG.items():
    env_value = os.environ.get(key)
    if env_value is not None:
        try:
            if isinstance(value, number_type):
                set(key, int(env_value))
            elif isinstance(value, float):
                set(key, float(env_value))
            elif isinstance(value, string_type):
                set(key, str(env_value))
        except:pass

def load_conf(filename):
    try:
        with open(filename, "r") as fp:
            conf_content = StringIO("[global]\n" + fp.read())
            cf = configparser.ConfigParser(allow_no_value=True)
            cf._read(conf_content, filename)

            for key, value in DEFAULT_CONFIG.items():
                if key.startswith("STORE_"):
                    conf_value = cf.get("store", key[6:].lower())
                elif key.startswith("ACTION_"):
                    conf_value = cf.get("action", key[7:].lower())
                elif key.startswith("EXTENSION"):
                    if key == "EXTENSIONS":
                        conf_value = cf.get("extension", "extensions")
                        if isinstance(conf_value, string_type):
                            set(key, conf_value.split(";"))
                            continue
                    else:
                        conf_value = cf.get("extension", key[10:].lower())
                else:
                    conf_value = cf.get("global", key.lower())

                try:
                    if isinstance(value, number_type):
                        set(key, int(conf_value))
                    elif isinstance(value, float):
                        set(key, float(conf_value))
                    elif isinstance(value, string_type):
                        set(key, str(conf_value))
                except:
                    pass
    except IOError:
        raise ConfFileNotFoundError()