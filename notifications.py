
import urllib
import urllib2
import sys
import requests


FB_APP_ID = 498777246878058
FB_APP_NAME = 'The FAD Study'
FB_APP_SECRET = '02272a1ef565d2bbbec38c64e464094f'
friendID = 'mitchl.stewart'
access_token = 'CAAHFoqCfSWoBABw0xgVfa3Yv2jskjRtoNysKVvHLQW6vixD5sJcHim9Vc5TGrEQfP2YaMsFdr4fxYbkFjB234UO8OGamd2BzTP1JJzUZAnswQQ1aU1KCLVa9MakZBG3Acqz1Rh3upW5uKZBvIhplgmrqDVY5wvWqQ2tb9hBtZC6ANJH3F2T23gIr5y0wmcIZD'

# payload = {'client_id' : 498777246878058,
#           'client_secret' : '02272a1ef565d2bbbec38c64e464094f'}
# r = requests.post('https://graph.facebook.com/oauth/access_token/', params=payload)

# print r.url
# print r.text

payload = {'access_token' : '498777246878058|02272a1ef565d2bbbec38c64e464094f',
          'href' : '',
          'template' : 'Hey, time to rate your mood for today!'}
r = requests.post('https://graph.facebook.com/' + friendID + '/notifications', params=payload)

print r.url
print r.text
