#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://developers.google.com/accounts/docs/OpenID
# http://janrain.com/openid-enabled/

from openid.consumer import consumer
from openid.store import memstore

import urllib, urllib2, webbrowser, json
import BaseHTTPServer
from urlparse import urlparse
import util

port = 8000

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		host = self.headers.get('Host')
		url = 'http://' + host + self.path
		s = urlparse(self.path).query
		result = util.urldecode(s)

		session = {}
		store = memstore.MemoryStore()
		openid_consumer = consumer.Consumer(session, store)
		info = openid_consumer.complete(result, url)

		display_identifier = info.getDisplayIdentifier()

		# Copy from https://github.com/openid/python-openid/blob/master/examples/consumer.py
		if info.status == consumer.FAILURE and display_identifier:
			# In the case of failure, if info is non-None, it is the
			# URL that we were verifying. We include it in the error
			# message to help the user figure out what happened.
			fmt = "Verification of %s failed: %s"
			message = fmt % (display_identifier, info.message)
		elif info.status == consumer.SUCCESS:
			# Success means that the transaction completed without
			# error. If info is None, it means that the user cancelled
			# the verification.
			css_class = 'alert'

			# This is a successful verification attempt. If this
			# was a real application, we would do our login,
			# comment posting, etc. here.
			fmt = "You have successfully verified %s as your identity."
			message = fmt % (display_identifier,)
			if info.endpoint.canonicalID:
				# You should authorize i-name users by their canonicalID,
				# rather than their more human-friendly identifiers.  That
				# way their account with you is not compromised if their
				# i-name registration expires and is bought by someone else.
				message += ("  This is an i-name, and its persistent ID is %s"
							% (info.endpoint.canonicalID,))
		elif info.status == consumer.CANCEL:
			# cancelled
			message = 'Verification cancelled'
		elif info.status == consumer.SETUP_NEEDED:
			if info.setup_url:
				message = 'Setup needed : %s' % (info.setup_url,)
			else:
				# This means auth didn't succeed, but you're welcome to try
				# non-immediate mode.
				message = 'Setup needed'
		else:
			# Either we don't understand the code or there is no
			# openid_url included with the error. Give a generic
			# failure message. The library should supply debug
			# information in a log.
			message = 'Verification failed.'

		print message
		email = None
		for key in result:
			value = result[key]
			if value == 'http://axschema.org/contact/email':
				email_key = key.replace('type', 'value')
				email = result[email_key]
				break
		if email:
			print 'Your Email is : %s' % email

		result['message'] = message
		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self.end_headers()
		self.wfile.write(json.dumps(result, indent=4))

endpoint = 'https://www.google.com/accounts/o8/ud'
params = {
		'openid.return_to' : 'http://localhost:' + str(port),
		'openid.mode' : 'checkid_setup',
		'openid.ns' : 'http://specs.openid.net/auth/2.0',
		'openid.claimed_id' : 'http://specs.openid.net/auth/2.0/identifier_select',
		'openid.identity' : 'http://specs.openid.net/auth/2.0/identifier_select',
		}

google_exchange = {
		'openid.ns.ax' : 'http://openid.net/srv/ax/1.0',
		'openid.ax.mode' : 'fetch_request',
		'openid.ax.type.email' : 'http://axschema.org/contact/email',
		'openid.ax.required' : 'email',
		}

if __name__ == '__main__':
	params.update(google_exchange)

	url = endpoint + '?' + urllib.urlencode(params)

	print 'Start Server, Please wait ...'
	httpd = BaseHTTPServer.HTTPServer(('', port), RequestHandler)

	webbrowser.open(url)
	httpd.handle_request()
	httpd.server_close()
