import httplib, socket, base64, json, csv
from lxml import etree

class LetsGrowConnector():
    def __init__(self, username, password):
        self.info_url = 'moduleconfigurationservice.letsgrow.com'
        self.data_url = 'moduleconfigurationservice.letsgrow.com'
        self.sid = ''
        self.username = username
        self.password = password
        
    def login (self):
        heads = self.getAuthHeader(self.username, self.password)
        c = httplib.HTTPConnection(self.info_url, timeout=10)
        c.request('GET', '/PartnerInformation.svc/Login', '', heads)
        result = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        c.close()
        
#        self.log_response(status, headers, response)
        
        return response
        
    def getModuleTemplates (self):    
        heads = self.getAuthHeader(self.username, self.password)
        c = httplib.HTTPConnection(self.info_url, timeout=10)
        c.request('GET', '/PartnerInformation.svc/RetrieveModuleTemplates?sid={0}'.format(self.sid), '', heads)

        result = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        c.close()
        
 #       self.log_response(status, headers, response)
        
        return response
    
    def getModuleDefinitions (self, mtid):
        heads = self.getAuthHeader(self.username, self.password)
        c = httplib.HTTPConnection(self.info_url, timeout=10)
        c.request('GET', '/PartnerInformation.svc/RetrieveModuleDefinitions?sid={0}&moduleTemplateId={1}'.format(self.sid, mtid), '', heads)

        result = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        f = open('module_{0}.xml'.format(mtid), "w")
        f.write(response)
        f.close() 
        
        c.close()
        
 #       self.log_response(status, headers, response)
        
        return response

    def getModuleInformation (self, mid):
        heads = self.getAuthHeader(self.username, self.password)
        c = httplib.HTTPConnection(self.info_url, timeout=10)
        c.request('GET', '/PartnerInformation.svc/RetrieveModuleInformation?sid={0}&moduleId={1}'.format(self.sid, mid), '', heads)

        result = c.getresponse()        
        response = result.read()
        status   = result.status
        headers  = result.getheaders()
        
        f = open('sensors_{0}.xml'.format(mid), "w")
        f.write(response)
        f.close()
        
        c.close()
        
  #      self.log_response(status, headers, response)
        
        return response
    
    def getAuthHeader(self, username, password):
        authentication_string = '{0}:{1}'.format(username, password)
        authentication_string = base64.b64encode(authentication_string)
        return  {'Authorization': 'Basic {0}'.format(authentication_string)}
    
    def log_response(self, s, h, r):
        print '================================'
        print 'status: {0}'.format(s)
        print 'headers: {0}'.format(h)
        print 'response: {0}'.format(r)
        print '================================'
        
        
def makeTagName(ns, tag):
    return '{'+'{0}'.format(ns)+'}'+'{0}'.format(tag)
        
def csvExportSensors(s_list, filename):
    f = open(filename, 'w')
    
    for s in s_list:
#        line = u'{0},{1},{2},'.format(s['mtid'], s['mid'],s['colId']) + ',' + s['name'] + ',' + s['device_type'] + '/n'
        f.write(str(s['mtid']))
        f.write(';')
        f.write(str(s['mid']))
        f.write(';')
        f.write(str(s['colId']))
        f.write(';')
        f.write(s['name'].encode('utf-8'))
        f.write(';')
        try:
            f.write(s['device_type'].encode('utf-8'))
        except:
            pass
        f.write('\n')
        
    f.close()
    
sensors = []
        
L = LetsGrowConnector('greenformula', 'Jango2011')

# login and obtain session id
r = L.login()
root = etree.fromstring(r)
L.sid = root.text

# get list of module templates
r = L.getModuleTemplates()
templates = etree.fromstring(r)
ns = templates.nsmap[None]

# iterate over all module templates
for t in templates.iterchildren(tag=makeTagName(ns, 'PartnerModuleTemplate')):
    mtid = int(t.find(makeTagName(ns, 'Id')).text)
    print t.find(makeTagName(ns, 'Name')).text
    
    # obtain the module definitions for all module templates
    r = L.getModuleDefinitions(mtid)
    definitions = etree.fromstring(r)
    
    # iterate over all module definition
    for d in definitions.iterchildren(tag=makeTagName(ns, 'PartnerModule')):
        # for each definition, check if it is from the right customer
        if d.find(makeTagName(ns, 'LoginName')).text == 'T3126-0002':
            mid = int(d.find(makeTagName(ns, 'Id')).text)
            # for each module that belongs to the right customer, get additional information
            r = L.getModuleInformation(mid)
            information = etree.fromstring(r)
            
            # obtain all defined sensors for the module
            items = information.find(makeTagName(ns, 'ModuleItems'))
            for i in items.iterchildren(tag=makeTagName(ns, 'PartnerModuleItem')):
                sensor = {}
                sensor['mtid'] = mtid
                sensor['mid'] = mid
                sensor['colId'] = int(i.find(makeTagName(ns, 'ColId')).text)
                sensor['name'] = i.find(makeTagName(ns, 'Description')).text
                sensor['device_type'] = i.find(makeTagName(ns, 'CustomerDescription')).text
                sensors.append(sensor)

sensors_5min = []
for s in sensors:
    if 'FiveMinute' in s['name']:
        sensors_5min.append(s)



csvExportSensors(sensors, 'sensorslist_full.csv')
csvExportSensors(sensors_5min, 'sensorlist_5min.csv')
print json.dumps(sensors)
    