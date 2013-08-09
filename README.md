twitter-api-test
================

一个测试 Twitter API 的命令行小工具

在 <https://dev.twitter.com/apps> 上创建应用后，
修改 config.py 中的 consumer\_key 和 consumer\_secret 
为对应的值，就可以使用了。

比如：
	
	./twitter.py -p count=5 -p trim_user=true statuses/home_timeline

就可以获得用户的时间线，具体信息可以参考 [Twitter API](https://dev.twitter.com/docs/api/1.1/) ，
返回的是 JSON 格式，本程序只是简单的把它输出到控制台而已，可以将它重定向到 JSON 文件中：

	./twitter.py -p count=5 -p trim_user=true statuses/home_timeline >/tmp/test.json

然后用浏览器或者其他查看 JSON 的工具查看。

第一次使用时，会需要授权，程序会自动打开浏览器，授权之后，就会看到 PIN-Code ，
把它输入到控制台，回车即可。

可以参考：[Implementing Sign in with Twitter](https://dev.twitter.com/docs/auth/implementing-sign-twitter) ， [PIN-based authorization](https://dev.twitter.com/docs/auth/pin-based-authorization) ，
[Authorizing a request](https://dev.twitter.com/docs/auth/authorizing-request) 和 
[Creating a signature](https://dev.twitter.com/docs/auth/creating-signature)
， 生成的 Token 会储存到 config.json 中。

也可以使用 [Tokens from dev.twitter.com](https://dev.twitter.com/docs/auth/tokens-devtwittercom)
生成的 Token ，把对应的 access\_token 和 access\_token\_secret 配置到 config.py 就行了。

(PS: 本程序不自带翻墙功能，请使用 VPN 或其他翻墙工具)

[GitHub](http://developer.github.com/),
[GitHub OAuth](http://developer.github.com/v3/oauth)

[Facebook](https://developers.facebook.com),
[Graph API](https://developers.facebook.com/docs/reference/api/),
[The Login Flow for Web (without JavaScript SDK)](https://developers.facebook.com/docs/facebook-login/login-flow-for-web-no-jssdk),
[Access Tokens](https://developers.facebook.com/docs/facebook-login/access-tokens)

[Google](https://code.google.com/apis/console),
[Using OAuth 2.0 for Login](https://developers.google.com/accounts/docs/OAuth2Login),

[JSON Web Token (JWT)](http://openid.net/specs/draft-jones-json-web-token-07.html),
[JSON Web Signature (JWS)](http://tools.ietf.org/html/draft-jones-json-web-signature-04),
[Verifying signature in Python](http://stackoverflow.com/questions/5440550/verifying-signature-on-android-in-app-purchase-message-in-python-on-google-app-e)
