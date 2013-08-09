# -*- coding: utf-8 -*-

import config, json, os.path, urllib, sys, traceback, re

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
		# PS: 有时后测试的时候需要删除某条配置
		# 如果删除了最后一条就会出现
		# 新的最后一条后面多了一个逗号 ","
		# 导致 json 解析出错
		json_str = open(_json_file()).read()
		json_str = re.sub(r',\s*}$', '\n}', json_str)
		cf = json.loads(json_str)
		return cf
	except Exception:
		print >>sys.stderr, 'load json file Errer'
		traceback.print_exc()
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
	if config.facebook_access_token:
		cf['facebook_access_token'] = config.facebook_access_token
	if config.google_access_token:
		cf['google_access_token'] = config.google_access_token
	if config.google_id_token:
		cf['google_id_token'] = config.google_id_token
	if config.google_refresh_token:
		cf['google_refresh_token'] = config.google_refresh_token
	json.dump(cf, open(_json_file(), 'w'), indent=4)

def load_from_json():
	cf = _load_json_file()
	config.bearer = cf.get('bearer', config.bearer)
	config.access_token = cf.get('access_token', config.access_token)
	config.access_token_secret = cf.get('access_token_secret', config.access_token_secret)
	config.github_access_token = cf.get('github_access_token', config.github_access_token)
	config.facebook_access_token = cf.get('facebook_access_token', config.facebook_access_token)
	config.google_access_token = cf.get('google_access_token', config.google_access_token)
	config.google_id_token = cf.get('google_id_token', config.google_id_token)
	config.google_refresh_token = cf.get('google_refresh_token', config.google_refresh_token)

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
