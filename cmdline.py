#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, urllib2, json, os.path, sys, traceback, string
import config, oauth

prefix = 'https://api.twitter.com/1.1/'
suffix = '.json'
stream_resource = {
			'statuses/filter' : 'https://stream.twitter.com/1.1/statuses/filter.json', 
			'statuses/sample' : 'https://stream.twitter.com/1.1/statuses/sample.json',
			'statuses/firehose' : 'https://stream.twitter.com/1.1/statuses/firehose.json', 
			'user' : 'https://userstream.twitter.com/1.1/user.json',
			'site' : 'https://sitestream.twitter.com/1.1/site.json'}

access_token = None
access_token_secret = None

def _json_file():
	d = os.path.dirname(__file__)
	return os.path.join(d, 'config.json')

def _save_to_json():
	if access_token and access_token_secret:
		tmp = {}
		tmp['access_token'] = access_token
		tmp['access_token_secret'] = access_token_secret
		json.dump(tmp, open(_json_file(), 'w'))

def _load_from_json():
	tmp = json.load(open(_json_file()))
	return tmp['access_token'], tmp['access_token_secret']

def init(force=False):
	global access_token, access_token_secret
	if force:
		access_token, access_token_secret = \
				oauth.authorize(config.consumer_key, config.consumer_secret)
	_save_to_json()
	if not access_token or not access_token_secret:
		try:
			access_token, access_token_secret = _load_from_json()
		except Exception:
			access_token, access_token_secret = \
					oauth.authorize(config.consumer_key, config.consumer_secret)
			_save_to_json()

parser = argparse.ArgumentParser(
		description='A Tool For Test Twitter API https://dev.twitter.com/docs/api/1.1')

parser.add_argument('-m', '--method', type=str, default='GET', 
		help='HTTP Method, default GET, you can use "get" or "post"')
parser.add_argument('-p', '--params', type=str, action='append', 
		help='HTTP Params, Format name=value, you can set many times, \
				like "-p count=1 -p trim_user=true"')
parser.add_argument('url', type=str, help='URL for Twitter API, like "statuses/home_timeline"')

args = parser.parse_args()

try:
	init()
except urllib2.HTTPError, e:
	print >>sys.stderr, '%s %s' % (e.code, e.msg)
	print >>sys.stderr, e.fp.read()
	traceback.print_exc()
	sys.exit(1)

is_stream = False
url = args.url
method = args.method
params = None

if url in stream_resource:
	url = stream_resource[url]
	params = {'delimited':'length'}
	is_stream = True
else:
	if not url.startswith('https://'):
		if url in stream_resource:
			url = stream_resource[url]
			is_stream = True
		else:
			url = prefix + url
	if not url.endswith('.json'):
		url = url + suffix

if args.params:
	params = {}
	for s in args.params:
		i = s.index('=')
		name = s[:i]
		value = s[i+1:]
		params[name] = value

def build_request(url, method, params):
	if method.upper() == 'GET':
		return oauth.build_request(url, method,
				config.consumer_key, config.consumer_secret,
				access_token, access_token_secret, 
				query_params=params)
	else:
		return oauth.build_request(url, method,
				config.consumer_key, config.consumer_secret,
				access_token, access_token_secret, 
				body_params=params)

try:
	req = build_request(url, method, params)
	response = urllib2.urlopen(req)
	if is_stream:
		len_str = ''
		while True:
			c = response.read(1)
			if c in string.digits:
				len_str += c
			if len_str and c == '\n':
				length = int(len_str)
				len_str = ''
				print response.read(length)
	else:
		print response.read()
except urllib2.HTTPError, e:
	print >>sys.stderr, '%s %s' % (e.code, e.msg)
	print >>sys.stderr, e.fp.read()
	traceback.print_exc()
