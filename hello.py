import urllib, urllib2, base64, json
from flask import Flask, url_for, request, redirect, session, jsonify, Response, make_response
app = Flask(__name__)

myState = 'AdventureTime'

@app.route('/')
def index():
    return "Hello!<p/> This is a simple Dropbox client!<p/> Click " \
	   " <a href= " + url_for('login') + ">here</a> to go to continue! </body>"

@app.route('/login')
def login():
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    args = {
	    'secret': app.secret_key,
	    'state': myState,
	}

    if state != myState:
		return redirect("https://www.dropbox.com/1/oauth2/authorize?client_id=" + args["secret"] + "&response_type=code&redirect_uri=http://127.0.0.1:5000/login&state=" + args["state"])
    else:
	session['code'] = code
	
	try:
		url = 'https://api.dropbox.com/1/oauth2/token'
		values = {'code' : code,
				'grant_type' : 'authorization_code',
				'redirect_uri' : 'http://127.0.0.1:5000/login',
				'client_id': 'fj3we96msh3hj34',
				'client_secret': 'zskj1k1blgsnm3l' } # need to greed
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		resp = urllib2.urlopen(req)
		dresp = json.loads(resp.read())
		session['access_token'] = dresp['access_token']
		session['uid'] = dresp['uid']
		return redirect(url_for('piclist'))
	except urllib2.HTTPError, error:
	    contents = error.read()
	    return "FAIL: "  + contents

@app.route('/piclist')
def piclist():
	try:
		url = 'https://api.dropbox.com/1/search/auto/'
		values = {'query' : '.jpg'}
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		req.add_header('Authorization', 'Bearer ' + session['access_token'])
		resp = urllib2.urlopen(req)
		jrsp = resp.read()
		pics = json.loads(jrsp)

		answer = ''
		for pic in pics:
			if pic['is_dir'] == False:
				answer += "<a href=" + url_for('pic', fpath = pic['path']) + ">" + pic['path'] + "</a><p/>"

		if answer == '':
			return "There is no picture in your folders"
		else:
			return "Select pic for download:<p/>" + answer

	except urllib2.HTTPError, error:
		contents = error.read()
		return "FAIL: " + contents

@app.route('/pic')
def pic():
	fpath = request.args.get('fpath', '')
	if session['access_token'] == '':
		return redirect(url_for(''))
	if fpath != '':
		#url = 'https://api-content.dropbox.com/1/files/auto/001_Dark_Steam.jpg'
		url = 'https://api-content.dropbox.com/1/files/auto/' + fpath
		req = urllib2.Request(url)
		req.add_header('Authorization', 'Bearer ' + session['access_token'])
		response = urllib2.urlopen(req)
		mypic = response.read()
		resp = make_response(mypic)
		resp.headers['Content-Type'] = 'image/jpeg'
		resp.headers['Content-Disposition'] = 'attachment; filename=img.jpg' #make hash(path)
		return resp
	else:
		return redirect(url_for('piclist'))

#with app.test_request_context():
  #print url_for('index')
  #print url_for('login')
  #print url_for('login', next='/')
  #print url_for('profile', username='John Doe')

app.secret_key = 'fj3we96msh3hj34'

if __name__ == '__main__':
    app.run(debug=True)