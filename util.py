# -*- coding: utf-8 -*-

import config, json, os.path, urllib

def print_response(response):
    print '%s %s' % (response.getcode(), response.msg)
    print response.info()
    print 
    print response.read()

def _json_file():
	d = os.path.dirname(__file__)
	return os.path.join(d, 'config.json')

def _load_json_file():
	try:
		cf = json.load(open(_json_file()))
		return cf
	except Exception:
		return {}

def save_to_json():
	cf = _load_json_file()
	if config.bearer:
		cf['bearer'] = config.bearer
	if config.access_token:
		cf['access_token'] = config.access_token
	if config.access_token_secret:
		cf['access_token_secret'] = config.access_token_secret
	if config.github_access_token:
		cf['github_access_token'] = config.github_access_token
	json.dump(cf, open(_json_file(), 'w'), indent=4)

def load_from_json():
	cf = _load_json_file()
	config.bearer = cf.get('bearer', config.bearer)
	config.access_token = cf.get('access_token', config.access_token)
	config.access_token_secret = cf.get('access_token_secret', config.access_token_secret)
	config.github_access_token = cf.get('github_access_token', config.github_access_token)

def urldecode(value):
	if not value:
		return {}
	value = value.strip()
	if not value:
		return {}
	arr = value.split('&')
	result = {}
	for s in arr:
		i = s.index('=')
		key = s[:i]
		value = s[i+1:]
		key = urllib.unquote_plus(key)
		value = urllib.unquote_plus(value)
		result[key] = value
	return result
