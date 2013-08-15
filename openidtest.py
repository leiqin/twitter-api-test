#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://developers.google.com/accounts/docs/OpenID
# http://janrain.com/openid-enabled/
# https://github.com/openid/python-openid

from openid.consumer import consumer
from openid.store import memstore
from openid.consumer import discover

import webbrowser, json, argparse
import traceback, sys, os.path, cgitb
import BaseHTTPServer
from urlparse import urlparse
import util

google_endpoint_url = 'https://www.google.com/accounts/o8/ud'
port = 8000
return_to = 'http://localhost:' + str(port)
realm = None
if not realm:
	_pr = urlparse(return_to)
	realm = _pr.scheme + '://' + _pr.netloc

session = {}
store = memstore.MemoryStore()
openid_consumer = consumer.Consumer(session, store)

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			host = self.headers.get('Host')
			url = 'http://' + host + self.path
			s = urlparse(self.path).query
			result = util.urldecode(s)
			for key in result:
				value = result[key]
				result[key] = value.decode('utf-8')

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

			print
			print
			print message
			email_value_key = ('http://openid.net/srv/ax/1.0', 'value.email')
			firstname_value_key = ('http://openid.net/srv/ax/1.0', 'value.firstname')
			lastname_value_key = ('http://openid.net/srv/ax/1.0', 'value.lastname')
			country_value_key = ('http://openid.net/srv/ax/1.0', 'value.country')
			language_value_key = ('http://openid.net/srv/ax/1.0', 'value.language')
			if info.status == consumer.SUCCESS:
				if email_value_key in info.message.args:
					email = info.message.args[email_value_key]
					print 'Your Email is : %s' % email
				if firstname_value_key in info.message.args:
					firstname = info.message.args[firstname_value_key]
					print 'Your Firstname is : %s' % firstname
				if lastname_value_key in info.message.args:
					lastname = info.message.args[lastname_value_key]
					print 'Your Lastname is : %s' % lastname
				if country_value_key in info.message.args:
					country = info.message.args[country_value_key]
					print 'Your Country is : %s' % country
				if language_value_key in info.message.args:
					language = info.message.args[language_value_key]
					print 'Your Language is : %s' % language
			print
			print

			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps(result, indent=4))
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			self.send_response(500)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(cgitb.html(sys.exc_info(), context=10))

filename = os.path.basename(__file__)

description = """
A Tool For try Google OpenID https://developers.google.com/accounts/docs/OpenID .
Need install python-openid https://github.com/openid/python-openid
"""

usage="""
%(filename)s [-e] [-F] [-L] [-c] [-l] openid
%(filename)s [-e] [-F] [-L] [-c] [-l] -g
""" % {'filename' : filename}

parser = argparse.ArgumentParser(description=description, usage=usage)
parser.add_argument('-e', '--email', action='store_true',
		help='Get Email Address')
parser.add_argument('-F', '--firstname', action='store_true',
		help='Get Firstname')
parser.add_argument('-L', '--lastname', action='store_true',
		help='Get Lastname')
parser.add_argument('-c', '--country', action='store_true',
		help='Get Country')
parser.add_argument('-l', '--language', action='store_true',
		help='Get Language')
parser.add_argument('-g', '--login-with-google', action='store_true',
		help='Login with Google')
parser.add_argument('openid', type=str, nargs='?', 
		help="Your OpenID, you can provide your OpenID or set -g for login with Google")

if __name__ == '__main__':
	args = parser.parse_args()
	url = None

	if args.openid:
		openid_url = args.openid
		# Copy from https://github.com/openid/python-openid/blob/master/examples/consumer.py
		try:
			request = openid_consumer.begin(openid_url)
		except consumer.DiscoveryFailure, exc:
			fetch_error_string = 'Error in discovery: %s' % str(exc[0])
			print fetch_error_string
			traceback.print_exc()
		else:
			if request is None:
				msg = 'No OpenID services found for "%s"' % openid_url
				print msg
			else:
				# Then, ask the library to begin the authorization.
				# Here we find out the identity server that will verify the
				# user's identity, and get a token that allows us to
				# communicate securely with the identity server.
				
				#trust_root = realm
				#url = request.redirectURL(trust_root, return_to, immediate=False)
				pass
	elif args.login_with_google:
		google_endpoint = discover.OpenIDServiceEndpoint.fromOPEndpointURL(google_endpoint_url)
		request = openid_consumer.beginWithoutDiscovery(google_endpoint)
	else:
		parser.print_help()
		sys.exit(1)
	
	required = []
	if args.email or args.firstname or args.lastname or args.country or args.language:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'mode', 'fetch_request')
	if args.email:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.email', 'http://axschema.org/contact/email')
		required.append('email')
	if args.firstname:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.firstname', 'http://axschema.org/namePerson/first')
		required.append('firstname')
	if args.lastname:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.lastname', 'http://axschema.org/namePerson/last')
		required.append('lastname')
	if args.country:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.country', 'http://axschema.org/contact/country/home')
		required.append('country')
	if args.language:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'type.language', 'http://axschema.org/pref/language')
		required.append('language')
	if required:
		request.addExtensionArg('http://openid.net/srv/ax/1.0', 'required', ','.join(required))

	url = request.redirectURL(realm, return_to, immediate=False)
	if not url:
		raise Exception('Authenticate url is None')

	print 'Start Server, Please wait ...'
	httpd = BaseHTTPServer.HTTPServer(('', port), RequestHandler)

	webbrowser.open(url)
	httpd.handle_request()
	httpd.server_close()
