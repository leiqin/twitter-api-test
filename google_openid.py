#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://developers.google.com/accounts/docs/OpenID

import urllib, urllib2, webbrowser
import BaseHTTPServer
from urlparse import urlparse
import util

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		s = urlparse(self.path).query
		result = util.urldecode(s)
		print result
		self.wfile.write(result)

url = 'https://www.google.com/accounts/o8/ud'
params = {
		'openid.return_to' : 'http://localhost:8000',
		'openid.mode' : 'checkid_setup',
		'openid.ns' : 'http://specs.openid.net/auth/2.0',
		'openid.claimed_id' : 'http://specs.openid.net/auth/2.0/identifier_select',
		'openid.identity' : 'http://specs.openid.net/auth/2.0/identifier_select',

		'openid.ns.ax' : 'http://openid.net/srv/ax/1.0',
		'openid.ax.mode' : 'fetch_request',
		'openid.ax.required' : 'country,email,firstname,language,lastname',
		}

url = url + '?' + urllib.urlencode(params)

print 'Start Server, Please wait ...'
httpd = BaseHTTPServer.HTTPServer(('', 8000), RequestHandler)

webbrowser.open(url)
httpd.handle_request()
httpd.server_close()
