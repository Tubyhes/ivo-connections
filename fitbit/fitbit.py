import httplib, socket, json, oauth.oauth as oauth, urlparse

class FitbitClient ():
    def __init__(self, consumer_key, consumer_secret):
        self.__oauth_consumer__ = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.__base_url__ = 'api.fitbit.com'
        self.__response__ = ''
        
    def get_response (self):
        return self.__response__
        
    def authenticate (self, user_id, oauth_token, oauth_token_secret):
        self.__user_id__ = user_id
        self.__oauth_token__ = oauth.OAuthToken(oauth_token, oauth_token_secret)
        
    def getActivities (self, day):
        url = '/1/user/{0}/activities/date/{1}.json'.format(self.__user_id__, day)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.__oauth_consumer__,\
                                                                   token=self.__oauth_token__,\
                                                                   http_method='GET',\
                                                                   http_url='http://api.fitbit.com{0}'.format(url))
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.__oauth_consumer__, self.__oauth_token__)

        c = httplib.HTTPConnection(self.__base_url__)
        
        method = 'GET'
        heads = oauth_request.to_header()
        body = ''
        
        c.request(method, url, body, heads)
        
        result   = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.__base_url__+url, method, heads, body)
        self.log_response(status, headers, response)
        
        if status == 200:
            self.__response__ = response
            return True
        else:
            self.__response__ = ''
            return False
        
    def subscribe (self, subscription_id):
        url = '/1/user/{0}/activities/apiSubscriptions/{1}.json'.format(self.__user_id__, subscription_id)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.__oauth_consumer__,\
                                                                   token=self.__oauth_token__,\
                                                                   http_method='POST',\
                                                                   http_url='http://api.fitbit.com{0}'.format(url))
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.__oauth_consumer__, self.__oauth_token__)

        c = httplib.HTTPConnection(self.__base_url__)
        
        method =  'POST'
        heads  = oauth_request.to_header()
        body   = ''
        
        c.request(method, url, body, heads)
        
        result   = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.__base_url__+url, method, heads, body)
        self.log_response(status, headers, response)

    def list_subscriptions (self):
        url = '/1/user/{0}/activities/apiSubscriptions.json'.format(self.__user_id__)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.__oauth_consumer__,\
                                                                   token=self.__oauth_token__,\
                                                                   http_method='GET',\
                                                                   http_url='http://api.fitbit.com{0}'.format(url))
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.__oauth_consumer__, self.__oauth_token__)

        c = httplib.HTTPConnection(self.__base_url__)
        
        method =  'GET'
        heads  = oauth_request.to_header()
        body   = ''
        
        c.request(method, url, body, heads)
        
        result   = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.__base_url__+url, method, heads, body)
        self.log_response(status, headers, response)   
    
    def getRequestToken (self, callback):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.__oauth_consumer__,\
                                                                   http_method = 'POST',\
                                                                   callback=callback,\
                                                                   http_url='http://api.fitbit.com/oauth/request_token')
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.__oauth_consumer__, None)
        
        c = httplib.HTTPSConnection(self.__base_url__)
        
        url ='/oauth/request_token'
        method = 'POST'
        heads = oauth_request.to_header()
        body = ''
        
        c.request(method, url, body, heads)
        
        result   = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.__base_url__+url, method, heads, body)
        self.log_response(status, headers, response)

        r = urlparse.parse_qs(response)
        self.__oauth_token__ = oauth.OAuthToken(r['oauth_token'][0], r['oauth_token_secret'][0])

    def getAccessToken (self, token, token_secret, verifier):
        self.__oauth_token__ = oauth.OAuthToken(token, token_secret)
        self.__oauth_token__.set_verifier(verifier)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.__oauth_consumer__,\
                                                                   token=self.__oauth_token__,\
                                                                   verifier=verifier,\
                                                                   http_method='POST',\
                                                                   http_url='http://api.fitbit.com/oauth/access_token')
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.__oauth_consumer__, self.__oauth_token__)
        
        c = httplib.HTTPSConnection(self.__base_url__)
        
        url ='/oauth/access_token'
        method = 'POST'
        heads = oauth_request.to_header()
        body = ''
        
        c.request(method, url, body, heads)
        
        result   = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.__base_url__+url, method, heads, body)
        self.log_response(status, headers, response)
        
        r = urlparse.parse_qs(response)
        self.__oauth_token__ = oauth.OAuthToken(r['oauth_token'][0], r['oauth_token_secret'][0])
        self.__user_id__ = r['encoded_user_id'][0]
        
    def log_request(self, u, m, h, b):
        print '================================'
        print 'url: http://' + u
        print 'method: ' + m
        print 'headers: {0}'.format(h) 
        print 'body: ' + b
        print '================================'
        
    def log_response(self, s, h, r):
        print '================================'
        print 'status: {0}'.format(s)
        print 'headers: {0}'.format(h)
        print 'response: {0}'.format(r)
        print '================================'
        
