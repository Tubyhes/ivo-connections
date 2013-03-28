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
import threading, json
import logging_sense, fitbit


main_page = '' +\
'<html>' +\
    '<head>' +\
        '<title>Sense Fitbit Signup</title>' +\
    '</head>' +\
    '<body>' +\
        '<h1>Sense Fitbit Signup</h1>' +\
        '<p>Here you can sign yourself up for data synchronization from Fitbit to Commonsense</p>' +\
    '</body>' +\
'</html>'    

class Reception():

    def __init__(self, host, port):
        self.logger = logging_sense.Logger()
        self.logger.setErrorLoggingOn()
        self.logger.setErrorPrefix('fitbit.reception')
        self.logger.setAccessLoggingOn()
        self.logger.setAccessPrefix('fitbit.reception')
        self.logger.setDebugLoggingOn()
        
        self.__port = port
        self.__host = host
        
        f = open('fitbit_oauth_consumer.txt', 'r')
        creds = json.load(f)
        f.close()
        self.__F = fitbit.FitbitClient(creds['oauth_consumer_key'], creds['oauth_consumer_secret'])
        
        self.__server = make_server(self.__host, self.__port, self.__handle_request__)
        self.__server.serve_forever()
            
    def __handle_request__(self, environ, start_response):
        # preferably here some anti-spam mechanism... need to check if this is a reasonable request
        response_status     = '500 Internal Server Error'
        response_body       = ''
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        url     = environ.get('PATH_INFO', '/')
        method  = environ.get('REQUEST_METHOD', 'GET')
        
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except:
            request_body_size = 0
        
        if request_body_size > 0:
            request_body = environ['wsgi.input'].read(request_body_size)
        else:
            request_body = ''
        
        self.logger.debug('url: ' + url)
        
        if url == '/':
            response_status = '200 OK'
            response_body   = main_page
            response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]

        elif url == '/notification':
            self.logger.debug('body: ' + request_body)
            notifications = json.loads(request_body)
            
            for notification in notifications:
                f = open('users/{0}.txt'.format(notification['subscriptionId']), 'r')
                user_settings = json.load(f)
                f.close()
            
                self.__F.authenticate(user_settings['credentials']['user_id'], user_settings['credentials']['oauth_token'], user_settings['credentials']['oauth_token_secret'])
                self.__F.getActivities(notification['date'])
                
#        elif url == '/register':
#            if method == 'POST':
#                try:
#                    p = threading.Thread(target=self.handle_register, args=[request_body])
#                    p.start()
#                except:
#                    pass
#                response_status, response_headers, response_body = self.register_response(request_body)
#            else:
#                response_status     = '405 Method Not Allowed'
#                response_body       = ''
#                response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
#                
#        elif url == '/in':
#            if method == 'POST':
#                try:
#                    p = threading.Thread(target=self.handle_in, args=[request_body])
#                    p.start()
#                except:
#                    pass
#                response_status, response_headers, response_body = self.in_response(request_body)
#            else:
#                response_status     = '405 Method Not Allowed'
#                response_body       = ''
#                response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]           
#                 
#        elif url == '/out':
#            if method == 'GET':
#                try:
#                    p = threading.Thread(target=self.handle_out, args=[request_body])
#                    p.start()
#                except:
#                    pass
#                response_status, response_headers, response_body = self.out_response(request_body)
#            else:
#                response_status     = '405 Method Not Allowed'
#                response_body       = ''
#                response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]         
#                   
        else:
            response_status, response_headers, response_body = self.__not_found__()
                
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
        

R = Reception('localhost', 80)

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