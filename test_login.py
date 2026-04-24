import json, urllib.request, urllib.error
try:
    req = urllib.request.Request('http://127.0.0.1:8000/login', method='POST', headers={'Content-Type': 'application/json'}, data=json.dumps({'email':'admin@vala.com','password':'12345'}).encode('utf-8'))
    res = urllib.request.urlopen(req)
    print(res.read().decode())
except urllib.error.HTTPError as e:
    print(e.read().decode())
