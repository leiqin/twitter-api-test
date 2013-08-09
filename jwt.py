# -*- coding: utf-8 -*-
# http://openid.net/specs/draft-jones-json-web-token-07.html
# http://tools.ietf.org/html/draft-jones-json-web-signature-04
"""
支持 plaintext 和 signed (JWS) 的 JWT
不支持嵌套
JWS 的算法支持：HS256, HS384, HS512
"""

import base64, json, hmac, hashlib


algorithms = ['none', \
		'HS256', 'HS384', 'HS512']

# Base 64 -> Base 64 url encode
# http://kjur.github.io/jsjws/tool_b64uenc.html
#   '+'   ->   '-'
#   '/'   ->   '_'
def base64urldecode(value):
	i = len(value) % 4
	if i != 0:
		value += '=' * (4 - i)
	value = value.replace('-', '+').replace('_', '/')
	return base64.decodestring(value)

def base64urlencode(value):
	result = base64.encodestring(value).replace('\n', '')
	result = result.replace('+', '-').replace('/', '_')
	if result.endswith('=='):
		result = result[:-2]
	if result.endswith('='):
		result = result[:-1]
	return result

def toJWT(jsonobj, alg='none',key=None):
	if alg not in algorithms:
		raise Exception(u'不支持的算法 %s' % alg)
	header = {'typ':'JWT', 'alg':alg}
	header = json.dumps(header)
	header = base64urlencode(header)
	message = json.dumps(jsonobj)
	message = base64urlencode(message)
	
	if alg == 'none':
		return header + '.' + message + '.'

	if alg.startswith('HS'):
		if key is None:
			raise Exception('key is None')
		algorithm = 'sha' + alg[2:]
		method = getattr(hashlib, algorithm)
		jws_signing_input = header + '.' + message
		HMAC = hmac.new(key, jws_signing_input, method)
		signature = HMAC.digest()
		third = base64urlencode(signature)
		return jws_signing_input + '.' + third

	raise Exception(u'不支持的算法 %s' % alg)

def _toJSON(value):
	value = base64urldecode(value)
	return json.loads(value)

def toJSON(jwt, key=None):
	first, second, third = jwt.split('.')
	header = _toJSON(first)
	alg = header['alg']
	if alg not in algorithms:
		raise Exception(u'不支持的算法 %s' % alg)

	if alg == 'none':
		return _toJSON(second)

	if alg.startswith('HS'):
		if key is None:
			raise Exception('key is None, alg %s need a key' % alg)
		algorithm = 'sha' + alg[2:]
		method = getattr(hashlib, algorithm)
		jws_signing_input = first + '.' + second
		HMAC = hmac.new(key, jws_signing_input, method)
		signature = HMAC.digest()
		if base64urldecode(third) == signature:
			return _toJSON(second)
		else:
			raise Exception('validate fail')

	raise Exception(u'不支持的算法 %s' % alg)
