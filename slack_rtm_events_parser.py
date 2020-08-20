# Utility Script for getting a list of all rtm events

import urllib.request as urllib2

from bs4 import BeautifulSoup

url = "https://api.slack.com/rtm"
soup = BeautifulSoup(urllib2.urlopen(url).read(), features="lxml")

table3 = soup.find_all("tr")
slack_rtm_events = []

for tr in table3[1:]:
    first_column = tr.findAll("td")[0].getText()
    slack_rtm_events.append(first_column)

print(slack_rtm_events)
