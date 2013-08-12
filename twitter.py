#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, urllib2, sys, traceback, string, os.path
import config, oauth, util, application_only_authentication

prefix = 'https://api.twitter.com/1.1/'
suffix = '.json'
stream_resource = {
			'statuses/filter' : 'https://stream.twitter.com/1.1/statuses/filter.json', 
			'statuses/sample' : 'https://stream.twitter.com/1.1/statuses/sample.json',
			'statuses/firehose' : 'https://stream.twitter.com/1.1/statuses/firehose.json', 
			'user' : 'https://userstream.twitter.com/1.1/user.json',
			'site' : 'https://sitestream.twitter.com/1.1/site.json'}

def init(app_only=False, force=False):
	if force:
		if app_only:
			config.twitter_bearer = application_only_authentication.get_assess_token(
					config.twitter_consumer_key, config.twitter_consumer_secret)
		else:
			config.twitter_access_token, config.twitter_access_token_secret = \
					oauth.authorize(config.twitter_consumer_key, config.twitter_consumer_secret)
		util.save_to_json()

	if app_only:
		if not config.twitter_bearer:
			util.load_from_json()
		if not config.twitter_bearer:
			config.twitter_bearer = application_only_authentication.get_assess_token(
					config.twitter_consumer_key, config.twitter_consumer_secret)
			util.save_to_json()
	else:
		if not config.twitter_access_token or not config.twitter_access_token_secret:
			util.load_from_json()
		if not config.twitter_access_token or not config.twitter_access_token_secret:
			config.twitter_access_token, config.twitter_access_token_secret = \
					oauth.authorize(config.twitter_consumer_key, config.twitter_consumer_secret)
			util.save_to_json()

def build_request(url, method, params, app_only=False):
	if app_only:
		if method.upper() == 'GET':
			return application_only_authentication.build_request(url, method,
					config.twitter_bearer, query_params=params)
		else:
			return application_only_authentication.build_request(url, method,
					config.twitter_bearer, body_params=params)
	else:
		if method.upper() == 'GET':
			return oauth.build_request(url, method,
					config.twitter_consumer_key, config.twitter_consumer_secret,
					config.twitter_access_token, config.twitter_access_token_secret, 
					query_params=params)
		else:
			return oauth.build_request(url, method,
					config.twitter_consumer_key, config.twitter_consumer_secret,
					config.twitter_access_token, config.twitter_access_token_secret, 
					body_params=params)

filename = os.path.basename(__file__)

description = """
A Tool For Test Twitter API https://dev.twitter.com/docs/api/1.1
"""

usage="""
%(filename)s [-a] [-m method] [-p name=value]... url
%(filename)s -c
""" % {'filename' : filename}

parser = argparse.ArgumentParser(description=description, usage=usage)

parser.add_argument('-a', '--app-only', action='store_true', dest='app_only',
		help="use Application-only authentication")
parser.add_argument('-m', '--method', type=str, default='GET', 
		help='HTTP Method, default GET, you can use "get" or "post"')
parser.add_argument('-p', '--params', type=str, action='append', 
		help='HTTP Params, Format name=value, you can set many times, \
				like "-p count=1 -p trim_user=true"')
parser.add_argument('-c', '--clean', action='store_true',
		help='Clean access_token if it exists')
parser.add_argument('url', type=str, nargs='?',
		help='URL for Twitter API, like "statuses/home_timeline" or "account/settings"')

if __name__ == '__main__':
	args = parser.parse_args()
	if args.clean:
		if args.app_only:
			config.twitter_bearer = ''
		else:
			config.twitter_access_token = ''
			config.twitter_access_token_secret = ''
		util.save_to_json()
	elif not args.url:
		parser.print_help()
	else:
		is_stream = False
		url = args.url
		method = args.method
		params = None
		app_only = args.app_only

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

		try:
			init(app_only)
			req = build_request(url, method, params, app_only)
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
