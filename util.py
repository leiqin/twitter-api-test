# -*- coding: utf-8 -*-

import config, json, os.path, urllib, sys, traceback, re

saved_config = ['twitter_bearer', 'twitter_access_token', 'twitter_access_token_secret',\
		'github_access_token', \
		'facebook_access_token', \
		'google_access_token', 'google_id_token', 'google_refresh_token']

def pprint(value):
	try:
		obj = json.loads(value)
		print json.dumps(obj, indent=4, ensure_ascii=False)
	except Exception:
		print value

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

def _set_config(cf, name):
	if not hasattr(config, name):
		print >>sys.stderr, 'Unknow config %s' % name
		return
	value = getattr(config, name)
	if value == '' and name in cf:
		del cf[name]
	if value:
		cf[name] = value

def _load_config(cf, name):
	value = cf.get(name, None)
	if value:
		setattr(config, name, value)

def save_to_json():
	cf = _load_json_file()
	for name in saved_config:
		_set_config(cf, name)
	json.dump(cf, open(_json_file(), 'w'), indent=4)

def load_from_json():
	cf = _load_json_file()
	for name in saved_config:
		_load_config(cf, name)

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
