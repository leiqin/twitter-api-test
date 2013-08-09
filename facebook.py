#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://developer.github.com

import argparse, urllib, urllib2, traceback, sys, webbrowser
import BaseHTTPServer
from urlparse import urlparse
import config, util

prefix = "https://graph.facebook.com/"
scope = None

state = "helloworld"
code = None

# You need to set your Website with Facebook Login to http://localhost:8000
# and App Domains to localhost
def authorize(app_id, app_secret):
	url = 'https://www.facebook.com/dialog/oauth'
	params = {'client_id' : app_id,
			'response_type' : 'code',
			'state' : state,
			'redirect_uri' : 'http://localhost:8000/'}
	if scope:
		params['scope'] = scope
	url = url + '?' + urllib.urlencode(params)

	print 'Need authorize, Start Server, Please wait ...'
	httpd = BaseHTTPServer.HTTPServer(('', 8000), RequestHandler)

	webbrowser.open(url)
	httpd.handle_request()
	httpd.server_close()

	if not code:
		raise Exception('Code is None')
	url = 'https://graph.facebook.com/oauth/access_token'
	params = {'client_id' : app_id,
			'client_secret' : app_secret,
			'redirect_uri' : 'http://localhost:8000/',
			'code' : code}
	url = url + '?' + urllib.urlencode(params)
	response = urllib2.urlopen(url)
	result = util.urldecode(response.read().strip())
	long_term_access_token = result['access_token']
	return long_term_access_token

def init():
	if not config.facebook_access_token:
		util.load_from_json()
	if not config.facebook_access_token:
		config.facebook_access_token = authorize(
				config.facebook_app_id, config.facebook_app_secret)
		util.save_to_json()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			s = urlparse(self.path).query
			result = util.urldecode(s)
			global code
			if result['state'] == state:
				code = result['code']
				self.wfile.write('Hello world')
			else:
				print self.path
				self.wfile.write(self.path)
		except Exception:
			print self.path
			self.wfile.write(self.path)

def _get_params(arr):
	if not arr:
		return {}
	params = {}
	for s in args.params:
		i = s.index('=')
		name = s[:i]
		value = s[i+1:]
		params[name] = value
	return params

parser = argparse.ArgumentParser(
		description='A Tool For test Facebook API \
				https://developers.facebook.com/docs/reference/api , \
				You need to set your Website with Facebook Login to \
				"http://localhost:8000" and App Domains to "localhost"') 
parser.add_argument('-p', '--params', type=str, action='append', 
		help='HTTP Params, Format name=value, you can set many times')
parser.add_argument('-m', '--method', type=str, default='GET', 
		help='HTTP Method, default GET')
parser.add_argument('url', type=str, help='URL For API, like "me"')

if __name__ == '__main__':
	try:
		args = parser.parse_args()
		url = args.url
		method = args.method.upper()
		if not url.startswith('https://'):
			url = prefix + url
		params = _get_params(args.params)
		init()
		params['access_token'] = config.facebook_access_token
		if method == 'GET':
			url = url + '?' + urllib.urlencode(params)
			req = urllib2.Request(url)
		elif method == 'POST' or method == 'PUT':
			req = urllib2.Request(url)
			req.data = urllib.urlencode(params)
			req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
			req.get_method = lambda: method
		else:
			url = url + '?' + urllib.urlencode(params)
			req = urllib2.Request(url)
			req.get_method = lambda: method

		response = urllib2.urlopen(req)
		print response.read()
	except urllib2.HTTPError, e:
		print >>sys.stderr, '%s %s' % (e.code, e.msg)
		print >>sys.stderr, e.fp.read()
		traceback.print_exc()