import httplib, socket, oauth.oauth as oauth

class FitbitAuthorizer ():
    def __init__(self, consumer_key, consumer_secret):
        self.__oauth_consumer__ = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.__base_url__ = 'api.fitbit.com'
        
    def getRequestToken (self):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.__oauth_consumer__,\
                                                                   http_method = 'POST',\
                                                                   callback='http://fitbit.datawheel.sense-os.nl/oauth_callback',\
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
