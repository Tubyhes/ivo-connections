import httplib, socket, json


class AgriSensysConnector ():
    def __init__ (self, auth_string):
        self.auth_string = auth_string
        self.base_url = 'agrisensys.eu'
        
    def getDataChannels (self):
        body =  '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +\
                '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://agrisensys.eu:80/soap/service.php" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:soap-enc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >' +\
                '<SOAP-ENV:Body>' +\
                '<mns:getAvailableDataChannels xmlns:mns="http://agrisensys.eu:80/soap/service.php" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' +\
                '<auth xsi:type="xsd:string">' +\
                self.auth_string +\
                '</auth>' +\
                '</mns:getAvailableDataChannels>' +\
                '</SOAP-ENV:Body>' +\
                '</SOAP-ENV:Envelope>'
        
        c = httplib.HTTPConnection(self.base_url, timeout=10)
        
        url ='/soap/service.php'
        method = 'GET'
        heads = {}
        
        c.request(method, url, body, heads)
        
        result = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.base_url+url, method, heads, body)
        self.log_response(status, headers, response)
        
    def getChannelData (self, channel_id, start, end):
        body = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +\
               '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://agrisensys.eu:80/soap/service.php" xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:soap-enc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >' +\
               '<SOAP-ENV:Body>' +\
               '<mns:getMeasurements xmlns:mns="http://agrisensys.eu:80/soap/service.php" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' +\
               '<auth xsi:type="xsd:string">{0}</auth>'.format(self.auth_string) +\
               '<dataChannelID xsi:type="xsd:int">{0}</dataChannelID>'.format(channel_id) +\
               '<start xsi:type="xsd:string">{0}</start>'.format(start) +\
               '<end xsi:type="xsd:string">{0}</end>'.format(end) +\
               '</mns:getMeasurements>' +\
               '</SOAP-ENV:Body>' +\
               '</SOAP-ENV:Envelope>'
        
        c = httplib.HTTPConnection(self.base_url, timeout=10)
        
        url ='/soap/service.php'
        method = 'GET'
        heads = {}
        
        c.request(method, url, body, heads)
        
        result = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        c.close()
        
        self.log_request(self.base_url+url, method, heads, body)
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

f = open('agrisensys_auth.txt', 'r')
creds = json.load(f)
f.close(f)

A = AgriSensysConnector(creds['auth_string'])
A.getDataChannels()
A.getChannelData(64, '2012-11-18T00:00:00+01:00', '2012-11-19T00:00:00+01:00')


