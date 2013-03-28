import fitbit, json, senseapi, os, glob, datetime

def getUsers (file_dir):
    os.chdir(file_dir)
    file_list = glob.glob("*.txt")
    return file_list

def getFitbitClient ():
    f = open('fitbit_oauth_consumer.txt', 'r')
    creds = json.load(f)
    f.close()
    F = fitbit.FitbitClient(creds['oauth_consumer_key'], creds['oauth_consumer_secret'])
    return F

F = getFitbitClient()
users = getUsers('users/')

for user in users:
    f = open(user, 'r')
    user_settings = json.load(f)
    f.close()
    
    S = senseapi.SenseAPI()
    S.setVerbosity(True)
    S.AuthenticateSessionId(user_settings['credentials']['user_name'], senseapi.MD5Hash(user_settings['credentials']['password']))
    F.authenticate(user_settings['credentials']['user_id'], user_settings['credentials']['oauth_token'], user_settings['credentials']['oauth_token_secret'])
    
#    last_sync = datetime.datetime.strptime(user_settings, '%Y-%m-%d')
    
    F.getActivities('2013-03-17')

    F.subscribe(user.rstrip('.tx'))
    
    F.list_subscriptions()
