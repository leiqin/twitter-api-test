# -*- coding: utf-8 -*-
# http://openid.net/specs/draft-jones-json-web-token-07.html
# http://tools.ietf.org/html/draft-jones-json-web-signature-04
"""
支持 plaintext 和 signed (JWS) 的 JWT
不支持嵌套
JWS 的算法支持：HS256, HS384, HS512, RS256, RS384, RS512
使用 RS256, RS384, RS512 的算法需要安装 PyCrypto

使用方法：
	import jwt
	a = {"hello":"world"}
	token = jwt.toJWT(a, alg="HS256", key="secret")

	b = jwt.toJSON(token, key="secret")
"""

import base64, json, hmac, hashlib, importlib


algorithms = ['none', \
		'HS256', 'HS384', 'HS512', \
		'RS256', 'RS384', 'RS512']

# Base 64 -> Base 64 url encode
# http://kjur.github.io/jsjws/tool_b64uenc.html
#   '+'   ->   '-'
#   '/'   ->   '_'
def base64urldecode(value):
	i = len(value) % 4
	if i != 0:
		value += '=' * (4 - i)
	if isinstance(value, unicode):
		value = value.encode('utf-8')
	return base64.urlsafe_b64decode(value)

def base64urlencode(value):
	result = base64.urlsafe_b64encode(value)
	if result.endswith('=='):
		result = result[:-2]
	if result.endswith('='):
		result = result[:-1]
	return result

def toJWT(jsonobj, alg='none',key=None):
	"""
	对于 plaintext ， alg 为 none
		不需要 key
	对于 JWS ， alg 为 HS256, HS384, HS512
		需要指定 key
	对于 JWS ， alg 为 RS256, RS384, RS512
		key 需要能被 Crypto.PublicKey.RSA 导入
			rsa = Crypto.PublicKey.RSA.importKey(key)
	"""
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
			raise Exception('key is None, alg "%s" need a key' % alg)
		jws_signing_input = header + '.' + message
		algorithm = 'sha' + alg[2:]
		method = getattr(hashlib, algorithm)
		HMAC = hmac.new(key, jws_signing_input, method)
		signature = HMAC.digest()
		third = base64urlencode(signature)
		return jws_signing_input + '.' + third

	if alg.startswith('RS'):
		if key is None:
			raise Exception('key is None, alg "%s" need a key' % alg)
		jws_signing_input = header + '.' + message
		from Crypto.PublicKey import RSA
		from Crypto.Signature import PKCS1_v1_5
		algorithm = 'SHA' + alg[2:]
		SHA = importlib.import_module('Crypto.Hash.' + algorithm)
		rsa = RSA.importKey(key)
		h = SHA.new()
		h.update(jws_signing_input)
		verifier = PKCS1_v1_5.new(rsa)
		signature = verifier.sign(h)
		third = base64urlencode(signature)
		return jws_signing_input + '.' + third

	raise Exception(u'不支持的算法 %s' % alg)

def _part_toJSON(value):
	value = base64urldecode(value)
	return json.loads(value)

def toJSON(jwt, key=None):
	"""
	本方法不会验证 JWT 是否过期
	对于 plaintext ， alg 为 none
		不需要 key
	对于 JWS ， alg 为 HS256, HS384, HS512
		需要指定 key
	对于 JWS ， alg 为 RS256, RS384, RS512
		key 需要能被 Crypto.PublicKey.RSA 导入
			rsa = Crypto.PublicKey.RSA.importKey(key)
		此时 key 也可以是一个 callable，如果 JWT header 中有 kid 信息，
		就会调用 key(kid) 来获取真正的 key 。
		如果 key 是一个 callable 而 JWT header 中没有 kid ，会报错
	"""
	first, second, third = jwt.split('.')
	header = _part_toJSON(first)
	alg = header['alg']
	if alg not in algorithms:
		print alg
		raise Exception(u'不支持的算法 %s' % alg)

	if alg == 'none':
		return _part_toJSON(second)

	if alg.startswith('HS'):
		if key is None:
			raise Exception('key is None, alg %s need a key' % alg)
		jws_signing_input = first + '.' + second
		signature = base64urldecode(third)
		algorithm = 'sha' + alg[2:]
		method = getattr(hashlib, algorithm)
		HMAC = hmac.new(key, jws_signing_input, method)
		if HMAC.digest() == signature:
			return _part_toJSON(second)
		else:
			raise Exception('validate fail')

	# http://stackoverflow.com/questions/5440550/verifying-signature-on-android-in-app-purchase-message-in-python-on-google-app-e
	if alg.startswith('RS'):
		if key is None:
			raise Exception('key is None, alg "%s" need a key' % alg)
		jws_signing_input = first + '.' + second
		signature = base64urldecode(third)
		from Crypto.PublicKey import RSA
		from Crypto.Signature import PKCS1_v1_5
		algorithm = 'SHA' + alg[2:]
		SHA = importlib.import_module('Crypto.Hash.' + algorithm)
		if callable(key):
			kid = header.get('kid', None)
			if kid is None:
				raise Exception("key is a callable, but JWT header isn't has a 'kid'")
			real_key = key(kid)
			rsa = RSA.importKey(real_key)
		else:
			rsa = RSA.importKey(key)
		h = SHA.new()
		h.update(jws_signing_input)
		verifier = PKCS1_v1_5.new(rsa)
		if verifier.verify(h, signature):
			return _part_toJSON(second)
		else:
			raise Exception('validate fail')
		
	raise Exception(u'不支持的算法 %s' % alg)
