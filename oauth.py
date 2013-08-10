# -*- coding: utf-8 -*-
# https://dev.twitter.com/docs/auth/authorizing-request
# https://dev.twitter.com/docs/auth/creating-signature
# https://dev.twitter.com/docs/auth/tokens-devtwittercom
# https://dev.twitter.com/docs/auth/implementing-sign-twitter
# https://dev.twitter.com/docs/auth/pin-based-authorization

import time, urllib, string, random, hmac, hashlib, base64, urllib2, webbrowser, sys
import util

alphanumeric = string.lowercase + string.uppercase + string.digits

def _oauth_nonce():
	arr = []
	for i in range(random.randint(30, 50)):
		arr.append(random.choice(alphanumeric))
	return ''.join(arr)

def _convert_value(value):
	if isinstance(value, unicode):
		value = value.encode('utf-8')
	elif not isinstance(value, str):
		value = str(value)
	return value

def _update_params(params, target):
	if not target:
		return
	for key in target:
		value = target[key]
		key = _convert_value(key)
		value = _convert_value(value)
		key = urllib.quote_plus(key)
		value = urllib.quote_plus(str(value))
		params[key] = value

def _oauth_signature(url, method, consumer_secret, access_token_secret, oauth, query_params=None, body_params=None):
	params = {}
	_update_params(params, oauth)
	_update_params(params, query_params)
	_update_params(params, body_params)
	
	parameter_array = []
	for key in sorted(params):
		value = params[key]
		parameter_array.append(key + '=' + value)
	parameter_string = '&'.join(parameter_array)

	signature_base_string = method.upper() + '&' \
			+ urllib.quote_plus(url) + '&' \
			+ urllib.quote_plus(parameter_string)

	signature_key = consumer_secret + '&'
	if access_token_secret:
		signature_key += access_token_secret

	HMAC = hmac.new(signature_key, signature_base_string, hashlib.sha1)
	oauth_signature = base64.b64encode(HMAC.digest())
	return oauth_signature

def _oauth_header(oauth):
	arr = []
	for key in oauth:
		value = oauth[key]
		key = _convert_value(key)
		value = _convert_value(value)
		tmp = urllib.quote_plus(key) + '="' + urllib.quote_plus(value) + '"'
		arr.append(tmp)
	return 'OAuth ' + ','.join(arr)

def _parse_response(response):
	body = response.read().strip()
	return util.urldecode(body)

def build_request(url, method, consumer_key, consumer_secret, 
		access_token=None, access_token_secret=None,
		oauth=None, query_params=None, body_params=None):
	if oauth is None:
		oauth = {}
	oauth['oauth_consumer_key'] = consumer_key
	oauth['oauth_nonce'] = _oauth_nonce()
	oauth['oauth_signature_method'] = 'HMAC-SHA1'
	oauth['oauth_timestamp'] = int(time.time())
	if access_token and access_token_secret:
		oauth['oauth_token'] = access_token
	oauth['oauth_version'] = '1.0'
	oauth['oauth_signature'] = _oauth_signature(url, method, 
			consumer_secret, access_token_secret, oauth, query_params, body_params)

	real_url = url
	if query_params:
		real_url = real_url + '?' + urllib.urlencode(query_params)
	req = urllib2.Request(real_url)
	req.add_header('Authorization', _oauth_header(oauth))
	if method.upper() == 'POST':
		req.data = ''
	if body_params:
		req.data = urllib.urlencode(body_params)
		req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')

	return req

def _default_input_callback():
	print 'Please Enter PIN Code :',
	pin_code = None
	while not pin_code:
		pin_code = sys.stdin.readline().strip()
	print 'PIN Code is ' + pin_code
	return pin_code

def authorize(consumer_key, consumer_secret, input_callback=_default_input_callback):
	req = build_request( 'https://api.twitter.com/oauth/request_token', 'POST',
			consumer_key, consumer_secret,
			oauth={'oauth_callback':'oob'})
	response = urllib2.urlopen(req)
		
	result = _parse_response(response)
	requst_token = result['oauth_token']
	requst_token_secret = result['oauth_token_secret']
	oauth_callback_confirmed = bool(result['oauth_callback_confirmed'])
	webbrowser.open('https://api.twitter.com/oauth/authorize?oauth_token=' + requst_token)
	if oauth_callback_confirmed: 
		pin_code = input_callback()
	else:
		print 'oauth_callback_confirmed : %s' % oauth_callback_confirmed
		print 'requst_token : %s' % requst_token
		print 'requst_token_secret : %s' % requst_token_secret
		raise Exception("oauth_callback_confirmed is not true")

	req = build_request('https://api.twitter.com/oauth/access_token', 'POST',
			consumer_key, consumer_secret,
			access_token=requst_token, access_token_secret=requst_token_secret,
			body_params={'oauth_verifier':pin_code})
	response = urllib2.urlopen(req)
	result = _parse_response(response)
	access_token = result['oauth_token']
	access_token_secret = result['oauth_token_secret']
	#print 'access_token : %s' % access_token
	#print 'access_token_secret : %s' % access_token_secret
	return access_token, access_token_secret

if __name__ == '__main__':
	import config
	try:
		access_token, access_token_secret = authorize(config.twitter_consumer_key, config.twitter_consumer_secret)
		print 'access_token : %s' % access_token
		print 'access_token_secret : %s' % access_token_secret
	except urllib2.HTTPError, e:
		print '%s %s' % (e.code, e.msg)
		print e.fp.read()
