import fitbit, json, senseapi, os, glob

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
    S.AuthenticateSessionId(user_settings['user_name'], senseapi.MD5Hash(user_settings['password']))
    F.authenticate(user_settings['user_id'], user_settings['oauth_token'], user_settings['oauth_token_secret'])
    
    F.getActivities('2013-03-17')

