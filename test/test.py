from bs4 import BeautifulSoup
import requests, re

URL = "https://lists.olin.edu/mailman/roster/seamlist"
soup = BeautifulSoup(requests.get(URL).text)


emailpatt = re.compile("^\.\./options/seamlist/([^/]+\.olin\.edu)$")
for a in soup.find_all('a', href=emailpatt):
  print(emailpatt.search(a['href']).group(1).replace('--at--', '@'))
