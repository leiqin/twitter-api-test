#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://developer.github.com

import argparse, urllib, urllib2, traceback, sys, webbrowser, json
import BaseHTTPServer, base64
from urlparse import urlparse
import config, util

scope = "openid email"

state = "helloworld"
code = None

# You need to use the Client ID for installed applications 
# or the web applications set Your site to http://localhost:8000
# and your Authorized Redirect URIs to http://localhost:8000/oauth2callback
def authorize(client_id, client_secret):
	url = 'https://accounts.google.com/o/oauth2/auth'
	params = {'client_id' : client_id,
			'response_type' : 'code',
			'state' : state,
			'redirect_uri' : 'http://localhost:8000/oauth2callback'}
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
	url = 'https://accounts.google.com/o/oauth2/token'
	params = {'client_id' : client_id,
			'client_secret' : client_secret,
			'redirect_uri' : 'http://localhost:8000/oauth2callback',
			'grant_type' : 'authorization_code',
			'code' : code}
	req = urllib2.Request(url)
	req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
	req.data = urllib.urlencode(params)
	response = urllib2.urlopen(req)
	r = json.load(response)
	access_token = r['access_token']
	id_token = r['id_token']
	refresh_token = r['refresh_token']
	return access_token, id_token, refresh_token

def init():
	if not config.google_access_token or not config.google_id_token:
		util.load_from_json()
	if not config.google_access_token or not config.google_id_token:
		config.google_access_token, config.google_id_token, config.google_refresh_token \
				= authorize(config.google_client_id, config.google_client_secret)
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

def validate_id_token(id_token):
	url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?id_token=' + id_token
	response = urllib2.urlopen(url)
	return response.read()

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
		description='A Tool For test Google API \
				You need to use the Client ID for installed applications \
				or the web applications set Your site to http://localhost:8000 \
				and your Authorized Redirect URIs to http://localhost:8000/oauth2callback')

if __name__ == '__main__':
	try:
		args = parser.parse_args()
		init()
		print validate_id_token(config.google_id_token)
	except urllib2.HTTPError, e:
		print >>sys.stderr, '%s %s' % (e.code, e.msg)
		print >>sys.stderr, e.fp.read()
		traceback.print_exc()
