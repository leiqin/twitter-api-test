# -*- coding: utf-8 -*-

consumer_key = "Your Consumer key"
consumer_secret = "Your Consumer secret"
access_token = None
access_token_secret = None

try:
    from config_local import *
except ImportError:
    pass

