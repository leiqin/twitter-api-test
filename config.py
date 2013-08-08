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

# github
# http://developer.github.com
github_client_id = "Your GitHub App Client ID"
github_client_secret = "Your GitHub App Client Secret"

github_access_token = None

# facebook
# https://developers.facebook.com
facebook_app_id = "Your Facebook App ID"
facebook_app_secret = "Your Facebook App Secret"

facebook_access_token = None

try:
    from config_local import *
except ImportError:
    pass

