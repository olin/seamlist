
import os, random, string, requests, json, re

def get_subscriptions(EMAIL, LIST, PASS): 
	payload = {"email": EMAIL, "password": PASS, "othersubs": "List my other subscriptions"}
	r = requests.post("https://lists.olin.edu/mailman/options/" + LIST + "/" + EMAIL, data=payload)

	from BeautifulSoup import BeautifulSoup
	html = requests.get("https://lists.olin.edu/mailman/listinfo").text
	soup = BeautifulSoup(r.text)
	subs = []
	for li in soup.findAll('li'):
		subs.append(li.find('a')['href'][len('../../options/'):-(len(EMAIL)+3)])
	return subs

EMAIL = "timothy.ryan@students.olin.edu"
LIST = "carpediem"
PASS = "3X6ZS5K4FCBG0GXT"

print get_subscriptions(EMAIL, LIST, PASS)