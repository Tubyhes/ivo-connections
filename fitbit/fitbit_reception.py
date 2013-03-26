import reception

class fitbit_reception(reception.Reception):
    
    def initialize(self):
        self.logger.setErrorLoggingOn()
        self.logger.setErrorPrefix('fitbit.reception')
        self.logger.setAccessLoggingOn()
        self.logger.setAccessPrefix('fitbit.reception')
        self.logger.setDebugLoggingOn()

    # new user registration handling
    def handle_register(self, request_body):
        # request body should contain user oauth token stuff and commonsense stuff
        # register at fitbit for subscription with commonsense user id or so as subscription id
        # POST /<api-version>/user/-/<collection-path>/apiSubscriptions/<subscription-id>.<response-format>
        # save credentials for user for fitbit and commonsense

    # notification that a user has new data        
    def handle_in(self, request_body):
        # when new notification comes in, body should contain list of updated resources
        # loop over resources
        # for every resource, retrieve data from fitbit and upload to commonsense

    # website for users to register
    # this only returns a bunch of html with a form and stuff   
     def out_response(self, request_body):
        # set response parameters
        status              = '200 OK'
        #nice piece of html here with a signup form
        response_body       = '<html><body>Thank you!</body></html>'
        response_headers    = [('Content-Type', 'text/html'), ('Content-Length', str(len(response_body)))]
        
        # return the response
        return status, response_headers, response_body

    # need some procedure to check 