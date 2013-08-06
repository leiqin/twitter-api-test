# -*- coding: utf-8 -*-

import config, json, os.path

def print_response(response):
    print '%s %s' % (response.getcode(), response.msg)
    print response.info()
    print 
    print response.read()

def _json_file():
	d = os.path.dirname(__file__)
	return os.path.join(d, 'config.json')

def save_to_json(app_only=False):
	try:
		cf = load_from_json()
	except Exception:
		cf = {}
	if app_only:
		if config.bearer:
			cf['bearer'] = config.bearer
	else:
		if config.access_token:
			cf['access_token'] = config.access_token
		if config.access_token_secret:
			cf['access_token_secret'] = config.access_token_secret
	json.dump(cf, open(_json_file(), 'w'))

def load_from_json(app_only=False):
	cf = json.load(open(_json_file()))
	if app_only:
		config.bearer = cf['bearer']
	else:
		config.access_token = cf['access_token']
		config.access_token_secret = cf['access_token_secret']
	return cf
