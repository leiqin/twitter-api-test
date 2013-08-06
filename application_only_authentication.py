# -*- coding: utf-8 -*-
# https://dev.twitter.com/docs/auth/application-only-auth

import urllib, urllib2, base64, json

def _get_bearer_token_credentials(consumer_key, consumer_secret):
	RFC_1738_encoded_consumer_key =  urllib.quote_plus(consumer_key)
	RFC_1738_encoded_consumer_secret = urllib.quote_plus(consumer_secret)

	Bearer_token_credentials = \
					RFC_1738_encoded_consumer_key + ':' + RFC_1738_encoded_consumer_secret
	Base64_encoded_bearer_token_credentials = \
					base64.encodestring(Bearer_token_credentials).replace('\n', '')
	return Base64_encoded_bearer_token_credentials

def get_assess_token(consumer_key, consumer_secret):
	bearer_token_credentials = _get_bearer_token_credentials(consumer_key, consumer_secret)

	req = urllib2.Request('https://api.twitter.com/oauth2/token')
	req.add_header('Authorization', 'Basic ' + bearer_token_credentials)
	req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
	req.data = 'grant_type=client_credentials'

	response = urllib2.urlopen(req)

	result = json.load(response)
	if result['token_type'] == "bearer":
		access_token = result["access_token"]
		return access_token
	else:
		raise Exception('token type is not bearer')

def invalidateg_bearer_token(consumer_key, consumer_secret, access_token):
	bearer_token_credentials = _get_bearer_token_credentials(consumer_key, consumer_secret)

	req = urllib2.Request('https://api.twitter.com/oauth2/invalidate_token')
	req.add_header('Authorization', 'Basic ' + bearer_token_credentials)
	req.data = 'access_token=' + access_token

	urllib2.urlopen(req)

def build_request(url, method, bearer,
		query_params=None, body_params=None):
	real_url = url
	if query_params:
		real_url = real_url + '?' + urllib.urlencode(query_params)
	req = urllib2.Request(real_url)
	req.add_header('Authorization', 'Bearer ' + bearer)
	if method.upper() == 'POST':
		req.data = ''
	if body_params:
		req.data = urllib.urlencode(body_params)
		req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
	return req


if __name__ == '__main__':
	import config
	try:
		access_token = get_assess_token(config.consumer_key, config.consumer_secret)
		print 'access_token: ' + access_token
		#invalidateg_bearer_token(config.consumer_key, config.consumer_secret, access_token)

		req = build_request( 'https://api.twitter.com/1.1/statuses/user_timeline.json', 
				'GET', access_token, query_params={'count':100,'screen_name':'twitterapi'})
		response = urllib2.urlopen(req)
		print '%s %s' % (response.getcode(), response.msg)
		print response.info()
		print 
		print response.read()
	except urllib2.HTTPError, e:
		print '%s %s' % (e.code, e.msg)
		print e.fp.read()
