""" 
Copyright (C) [2013] Sense Observation Systems B.V.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 
http://www.apache.org/licenses/LICENSE-2.0
 
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from wsgiref.simple_server import make_server
import threading, json, sys, time, datetime, urlparse, httplib
import logging_sense, fitbit, senseapi

try:
    host = sys.argv[1]
except:
    print "Usage: 'python fitbit_reception.py host'"
    sys.exit(1)

main_page = '' +\
'<html>' +\
    '<head>' +\
        '<title>Sense Fitbit Signup</title>' +\
    '</head>' +\
    '<body>' +\
        '<h1>Sense Fitbit Signup</h1>' +\
        '<p>Here you can sign yourself up for data synchronization from Fitbit to Commonsense.</p>' +\
        '<h2>Provide Sense credentials:</h2>' +\
        '<form method="POST" action="http://localhost/sense_login">' +\
            '<table bordercolor="lightgray"><tr><td valign="bottom">' +\
                '<center>' +\
                    '<p>username:<input type="text" name="username"/><br>' +\
                    'password:<input type="password" name="password"/><br>' +\
                    '<input type="submit" value="login"/></p>' +\
                '</center></td></tr>' +\
            '</table>' +\
        '</form>' +\
        '</body>' +\
'</html>'    

class Reception():

    def load_page (self, page_name):
        f = open('html/{0}.html'.format(page_name), 'r')
        s = f.read()
        f.close()
        return s

    def trim_to_json (self, s):
        return '[' + s.partition('[')[2].rpartition(']')[0] + ']'

    def __init__(self, host, port):
        self.logger = logging_sense.Logger()
        self.logger.setErrorLoggingOn()
        self.logger.setErrorPrefix('fitbit.reception')
        self.logger.setAccessLoggingOn()
        self.logger.setAccessPrefix('fitbit.reception')
        self.logger.setDebugLoggingOn()
        
        self.__port = port
        self.__host = host
        
        f = open('sense_oauth_consumer.txt', 'r')
        creds = json.load(f)
        f.close()
        self.__sense_oauth_consumer_key__ = creds['oauth_consumer_key']
        self.__sense_oauth_consumer_secret__ = creds['oauth_consumer_secret']
        self.__sense_oauth_callback__ = creds['callback']
        
        f = open('fitbit_oauth_consumer.txt', 'r')
        creds = json.load(f)
        f.close()
        self.__fitbit_oauth_consumer_key__ = creds['oauth_consumer_key']
        self.__fitbit_oauth_consumer_secret__ = creds['oauth_consumer_secret']
        self.__fitbit_oauth_callback__ = creds['callback']
        
        self.__server = make_server(self.__host, self.__port, self.__handle_request__)
        self.__server.serve_forever()
            
    def __handle_request__(self, environ, start_response):
        self.logger.debug(environ)
        
        # preferably here some anti-spam mechanism... need to check if this is a reasonable request
        response_status     = '500 Internal Server Error'
        response_body       = ''
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        url     = environ.get('PATH_INFO', '/')
        method  = environ.get('REQUEST_METHOD', 'GET')
        query   = environ.get('QUERY_STRING', '')
        
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except:
            request_body_size = 0
        
        if request_body_size > 0:
            request_body = environ['wsgi.input'].read(request_body_size)
        else:
            request_body = ''
        
        self.logger.debug('url: ' + url)
        self.logger.debug('method: ' + method)
        self.logger.debug('query: ' + query)
        self.logger.debug('body: ' + request_body)
#
# REQUEST FOR MAIN PAGE
#
        if url == '/':
            if method == 'GET':
                response_status = '200 OK'
                response_body   = self.load_page('main_page')
                response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
            else:
                response_status  = '405 Method Not Allowed'
                response_body    = ''
                response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
                
#          
# START OF LOGIN PROCEDURE                
#            
        elif url == '/login_procedure':
            S = senseapi.SenseAPI()
            S.setVerbosity(True)
            
            S.OauthSetConsumer(str(self.__sense_oauth_consumer_key__), str(self.__sense_oauth_consumer_secret__))
            if not S.OauthGetRequestToken(str(self.__sense_oauth_callback__)):
                response_status     = '401 Unauthorized'
                response_body       = self.load_page('main_page_error')
                response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
                start_response(response_status, response_headers)
                return [response_body]
 
            request_token = S.__oauth_token__.key
            f = open('users/{}.txt'.format(request_token), 'w')
            f.write(S.__oauth_token__.secret)
            f.close()
 
            response_status     = '301 Redirect'
            response_body       = ''
            response_headers    = [('Location', 'http://api.sense-os.nl/oauth/authorize?oauth_token={0}'.format(request_token))]

#
# OAUTH CALLBACK FROM COMMONSENSE
#
        elif url == '/commonsense_oauth_callback':
        # obtain access token from CommonSense
            oauth_stuff     = urlparse.parse_qs(query)
            request_token   = oauth_stuff['oauth_token'][0]
            verifier        = oauth_stuff['oauth_verifier'][0]
            
            f = open('users/{0}.txt'.format(request_token), 'r')
            token_secret = f.read()
            f.close()
 
            S = senseapi.SenseAPI()
            S.setVerbosity(True)
            S.OauthSetConsumer(str(self.__sense_oauth_consumer_key__), str(self.__sense_oauth_consumer_secret__))
            S.OauthSetToken(str(request_token), str(token_secret), str(verifier))
            
            if not S.OauthGetAccessToken():
                response_status     = '401 Unauthorized'
                response_body       = self.load_page('main_page_error')
                response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
                start_response(response_status, response_headers)
                return [response_body]
 
            creds = {'credentials':{}, 'sensors':{}}
            creds['credentials']['sense_oauth_token_secret'] = S.__oauth_token__.secret
            
        # and create a sensor for fitbit activities
            if S.SensorsPost({'sensor': {'name':'fitbit_activities', 'display_name':'Fitbit Activities', 'device_type':'fitbit', 'data_type':'json'}}):
                creds['sensors']['fitbit_activities'] = S.getLocationId()
            
        # then move on to authenticating at Fitbit
            F = fitbit.FitbitClient(self.__fitbit_oauth_consumer_key__, self.__fitbit_oauth_consumer_secret__)
            F.getRequestToken('{0}_{1}'.format(self.__fitbit_oauth_callback__, S.__oauth_token__.key))
            creds['credentials']['fitbit_oauth_token_key']      = F.__oauth_token__.key
            creds['credentials']['fitbit_oauth_token_secret']   = F.__oauth_token__.secret
            
            f = open('users/{0}.txt'.format(S.__oauth_token__.key), 'w')
            f.write(json.dumps(creds, sort_keys=True, indent=4))
            f.close()

            response_status     = '301 Redirect'
            response_body       = ''
            response_headers    = [('Location', 'https://www.fitbit.com/oauth/authorize?oauth_token={0}'.format(creds['credentials']['fitbit_oauth_token_key']))]

#
# OAUTH CALLBACK FROM FITBIT
#
        elif url.find('/fitbit_oauth_callback') > -1:
        # obtain access token from Fitbit
            sense_token = url.rsplit('_', 1)[1]
            print 'sense token: ' + sense_token
            oauth_stuff     = urlparse.parse_qs(query)
            request_token   = oauth_stuff['oauth_token'][0]
            verifier        = oauth_stuff['oauth_verifier'][0]
            
            f = open('users/{0}.txt'.format(sense_token), 'r')
            creds = json.load(f)
            f.close()
            token_secret = creds['credentials']['fitbit_oauth_token_secret']
            
            F = fitbit.FitbitClient(self.__fitbit_oauth_consumer_key__, self.__fitbit_oauth_consumer_secret__)
            F.getAccessToken(request_token, token_secret, verifier)
            creds['credentials']['fitbit_oauth_token_key'] = F.__oauth_token__.key
            creds['credentials']['fitbit_oauth_token_secret'] = F.__oauth_token__.secret
            creds['credentials']['fitbit_user_id'] = F.__user_id__
            
            F.subscribe(sense_token)
            
            f = open('users/{0}.txt'.format(sense_token), 'w')
            f.write(json.dumps(creds, sort_keys=True, indent=4))
            f.close()
            
            response_status     = '200 OK'
            response_body       = self.load_page('register_success')
            response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
            
#            
# INCOMING NOTIFICATION FROM FITBIT
#
        elif url == '/notification':
            self.logger.debug('body: ' + request_body)
            notifications = json.loads(self.trim_to_json(request_body))
            
            for notification in notifications:
                try:
                    f = open('users/{0}.txt'.format(notification['subscriptionId']), 'r')
                    user_settings = json.load(f)
                    f.close()
                except:
                    continue
                
                F = fitbit.FitbitClient(self.__fitbit_oauth_consumer_key__, self.__fitbit_oauth_consumer_secret__)
                F.authenticate(user_settings['credentials']['fitbit_user_id'], user_settings['credentials']['fitbit_oauth_token_key'], user_settings['credentials']['fitbit_oauth_token_secret'])
                if not F.getActivities(notification['date']):
                    continue

                S = senseapi.SenseAPI()
                S.setVerbosity(True)
                S.AuthenticateOauth(notification['subscriptionId'], user_settings['credentials']['sense_oauth_token_secret'], self.__sense_oauth_consumer_key__, self.__sense_oauth_consumer_secret__)
                # construct timestamp
                timestamp = time.mktime(datetime.datetime.strptime(notification['date'], "%Y-%m-%d").timetuple())
                S.SensorDataPost(user_settings['sensors']['fitbit_activities'], {'data':[{'value':F.get_response(), 'date':timestamp}]})

            response_status  = '204 No Content'
            response_body    = ''
            response_headers = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
         
#
# PAGE NOT FOUND
#   
        else:
            response_status, response_headers, response_body = self.__not_found__()
                
#
# RETURN RESULT
#
        start_response(response_status, response_headers)
        return [response_body] 

    def __not_found__(self):
        # set response parameters
        status              = '404 Not Found'
        response_body       = ''
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        # return the response
        return status, response_headers, response_body
        
        
    def register_response(self, request_body):
        # set response parameters
        status              = '200 OK'
        response_body       = '<html><body>Thank you!</body></html>'
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        # return the response
        return status, response_headers, response_body

    def in_response(self, request_body):
        # set response parameters
        status              = '200 OK'
        response_body       = '<html><body>Thank you!</body></html>'
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        # return the response
        return status, response_headers, response_body

    def out_response(self, request_body):
        # set response parameters
        status              = '200 OK'
        response_body       = '<html><body>Thank you!</body></html>'
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        # return the response
        return status, response_headers, response_body
        

R = Reception(host, 80)

#
#class fitbit_reception(reception.Reception):
#    
#    def initialize(self):
#        self.logger.setErrorLoggingOn()
#        self.logger.setErrorPrefix('fitbit.reception')
#        self.logger.setAccessLoggingOn()
#        self.logger.setAccessPrefix('fitbit.reception')
#        self.logger.setDebugLoggingOn()
#
#    # new user registration handling
#    def handle_register(self, request_body):
#        # request body should contain user oauth token stuff and commonsense stuff
#        # register at fitbit for subscription with commonsense user id or so as subscription id
#        # POST /<api-version>/user/-/<collection-path>/apiSubscriptions/<subscription-id>.<response-format>
#        # save credentials for user for fitbit and commonsense
#
#    # notification that a user has new data        
#    def handle_in(self, request_body):
#        # when new notification comes in, body should contain list of updated resources
#        # loop over resources
#        # for every resource, retrieve data from fitbit and upload to commonsense
#
#    # website for users to register
#    # this only returns a bunch of html with a form and stuff   
#     def out_response(self, request_body):
#        # set response parameters
#        status              = '200 OK'
#        #nice piece of html here with a signup form
#        response_body       = '<html><body>Thank you!</body></html>'
#        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
#        
#        # return the response
#        return status, response_headers, response_body
#
#    # need some procedure to check 