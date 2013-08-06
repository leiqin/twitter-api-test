# -*- coding: utf-8 -*-

consumer_key = "Your Consumer key"
consumer_secret = "Your Consumer secret"
# oauth token
# https://dev.twitter.com/docs/auth/oauth
access_token = None
access_token_secret = None
# application_only_authentication token 
# https://dev.twitter.com/docs/auth/application-only-auth
bearer = None

try:
    from config_local import *
except ImportError:
    pass

