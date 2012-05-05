# Seamlist
# http://docs.python-requests.org/en/latest/
# http://flask.pocoo.org/docs/

import os, random, string, requests, json, re, fwolin

from flask import Flask, session, request, redirect, url_for, render_template
app = Flask(__name__)
Flask.secret_key = os.environ.get('FLASK_SESSION_KEY', 'test-key-please-ignore')

SEAMLIST_ID = 'seamlist'

# Database
# --------

import pymongo
from pymongo import Connection
MONGO_URI = os.environ.get('MONGOLAB_URI', 'mongodb://localhost/heroku_app2714532')
connection = Connection(MONGO_URI)
MONGO_DB = 'heroku_app2714532'
db = connection[MONGO_DB]

# Functions
# ---------

from bs4 import BeautifulSoup

html = requests.get("https://lists.olin.edu/mailman/listinfo").text
soup = BeautifulSoup(html)
lists = []
for row in soup.find('table', width='100%').findAll('tr')[5:]:
	lists.append({
	"id": row.find('a')['href'][len('listinfo/'):] or "",
	"title": row.find('strong').string or "",
	"description": row.findAll('td')[1].string or ""
	})

def get_seamlist_subscriptions():
	URL = "https://lists.olin.edu/mailman/roster/seamlist"
	soup = BeautifulSoup(requests.get(URL).text)

	emailpatt = re.compile("^\.\./options/seamlist/([^/]+\.olin\.edu)$")
	return [emailpatt.search(a['href']).group(1).replace('--at--', '@') for a in soup.find_all('a', href=emailpatt)]

def get_user_subscriptions(EMAIL, PASS, LIST):
	payload = {"email": EMAIL, "password": PASS, "othersubs": "List my other subscriptions"}
	r = requests.post("https://lists.olin.edu/mailman/options/" + LIST + "/" + EMAIL, data=payload)

	html = requests.get("https://lists.olin.edu/mailman/listinfo").text
	soup = BeautifulSoup(r.text)
	subs = []
	for li in soup.findAll('li'):
		subs.append(li.find('a')['href'][len('../../options/'):-(len(EMAIL)+3)])
	return subs

def unsubscribe_user(EMAIL, PASS, LIST):
	payload = {"language":"en", "email": EMAIL, "password": PASS, "login": "Log in"}
	r = requests.post("https://lists.olin.edu/mailman/options/" + LIST, data=payload)

	payload = {"unsub": "Unsubscribe", "unsubconfirm": "1"}
	r = requests.post("https://lists.olin.edu/mailman/options/"+LIST+"/"+EMAIL, data=payload, cookies=r.cookies)
	return r

def reset_all_user_passwords(EMAIL, OLDPASS, PASS, LIST):
	payload = {"language":"en", "email": EMAIL, "password": OLDPASS, "login": "Log in"}
	r = requests.post("https://lists.olin.edu/mailman/options/" + LIST, data=payload)

	payload = {"newpw": PASS, "confpw": PASS, "pw-globally": "1", "changepw": "Change My Password"}
	r = requests.post("https://lists.olin.edu/mailman/options/"+LIST+"/"+EMAIL, data=payload, cookies=r.cookies)
	return r

def subscribe_user(EMAIL, PASS, LIST):
	payload = {"email": EMAIL, "fullname": "", "pw": PASS, "pw-conf": PASS, "digest": 0, "email-button": "Subscribe"}
	r = requests.post("https://lists.olin.edu/mailman/subscribe/" + LIST, data=payload)
	return r

#a = db.users.insert({'email': 'timothy.ryan@students.olin.edu', 'uniqkey': '0456'})
def get_user_key(email):
	user = db.users.find_one({"email": email})
	if not user:
		key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
		user = {'email': email, 'key': key}
		db.users.insert(user)
	return user['key']

# Routes
# ------

@app.route("/")
def index():
	if not session.get('seamlist-active', False):
		# Refresh to make sure
		session['seamlist-active'] = session['email'] in get_seamlist_subscriptions()
		if not session['seamlist-active']:
			return render_template('inactive.html')

	# Index page
	subbed = get_user_subscriptions(session['email'], get_user_key(session['email']), SEAMLIST_ID)
	subs = [li for li in lists if li['id'] in subbed and li['id'] != SEAMLIST_ID]
	unsubs = [li for li in lists if li['id'] not in subbed and li['id'] != SEAMLIST_ID]
	return render_template('index.html', email=session['email'], key=get_user_key(session['email']), subs=subs, unsubs=unsubs)

@app.route("/unsubscribe", methods=['POST'])
def unsubscribe():
	r = unsubscribe_user(session['email'], get_user_key(session['email']), request.form['listid'])
	return 'Unsubscribed. <p><a href="/">Go back?</a><h4>Contents:</h4><pre>' + r.text

@app.route("/subscribe", methods=['POST'])
def subscribe():
	r = subscribe_user(session['email'], get_user_key(session['email']), request.form['listid'])
	return 'Subscription request sent. Check your inbox! <p><a href="/">Go back?</a><h4>Contents:</h4><pre>' + r.text

# Fwol.in Authentication
# ----------------------

# First-time logged in action.
def logged_in(newlogin):
	# See if we have access to the user's passwords.
	if not session.get('seamlist-active', False):
		session['seamlist-active'] = session['email'] in get_seamlist_subscriptions()
	# Auto-reset passwords.
	if newlogin and session['seamlist-active']:
		print('Resetting all passwords for ' + session['email'])
		reset_all_user_passwords(session['email'], get_user_key(session['email']), get_user_key(session['email']), SEAMLIST_ID)

fwolin.enable_auth(app, logged_in)

# Launch
# ------

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.debug = True
	app.run(host='0.0.0.0', port=port)
