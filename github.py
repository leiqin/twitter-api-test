#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://developer.github.com

import argparse, urllib, urllib2, traceback, sys, webbrowser
import BaseHTTPServer
from urlparse import urlparse
import config, util

prefix = "https://api.github.com/"
scope = None

state = 'helloworld'
code = None
# You need to set your application's callback URL to 'http://localhost:8000'
def authorize(client_id, client_secret):
	url = 'https://github.com/login/oauth/authorize'
	params = {'client_id' : client_id,
			'state' : state}
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
	url = 'https://github.com/login/oauth/access_token'
	params = {'client_id' : client_id,
			'client_secret' : client_secret,
			'code' : code}
	url = url + '?' + urllib.urlencode(params)
	response = urllib2.urlopen(url)
	result = util.urldecode(response.read().strip())
	access_token = result['access_token']
	return access_token

def init():
	if not config.github_access_token:
		util.load_from_json()
	if not config.github_access_token:
		config.github_access_token = authorize(
				config.github_client_id, config.github_client_secret)
		util.save_to_json()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			s = urlparse(self.path).query
			result = util.urldecode(s)
			if result['state'] == state:
				global code
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
		description='A Tool For test GitHub API http://developer.github.com/ , \
				you need to set the application\'s callback URL to \
				"http://localhost:8000" or set the github_access_token in config.py')
parser.add_argument('-p', '--params', type=str, action='append', 
		help='HTTP Params, Format name=value, you can set many times, \
				like "-p type=all -p sort=updated"')
parser.add_argument('url', type=str, help='URL For API, like "user/repos"')

if __name__ == '__main__':
	try:
		args = parser.parse_args()
		url = args.url
		if not url.startswith('https://'):
			url = prefix + url
		params = _get_params(args.params)
		init()
		params['access_token'] = config.github_access_token
		url = url + '?' + urllib.urlencode(params)
		response = urllib2.urlopen(url)
		print response.read()
	except urllib2.HTTPError, e:
		print >>sys.stderr, '%s %s' % (e.code, e.msg)
		print >>sys.stderr, e.fp.read()
		traceback.print_exc()
