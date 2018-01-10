#-*- coding: UTF-8 -*- 

from __future__ import unicode_literals
from __future__ import print_function
import sys;reload(sys);sys.setdefaultencoding('utf8')
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from TimeNormalizer import TimeNormalizer
import datetime
import time
from bs4 import BeautifulSoup
import caldav
from caldav.elements import dav, cdav
from lxml import etree
import requests
from requests.auth import HTTPBasicAuth

class iCloudConnector(object):

    icloud_url = "http://cal.trumind.net:8008"
    username = None
    password = None
    propfind_principal = (
        u'''<?xml version="1.0" encoding="utf-8"?><propfind xmlns='DAV:'>'''
        u'''<prop><current-user-principal/></prop></propfind>'''
    )
    propfind_calendar_home_set = (
        u'''<?xml version="1.0" encoding="utf-8"?><propfind xmlns='DAV:' '''
        u'''xmlns:cd='urn:ietf:params:xml:ns:caldav'><prop>'''
        u'''<cd:calendar-home-set/></prop></propfind>'''
    )

    def __init__(self, username, password, **kwargs):
        self.username = username
        self.password = password
        if 'icloud_url' in kwargs:
            self.icloud_url = kwargs['icloud_url']
        self.discover()
        self.get_calendars()

    # discover: connect to icloud using the provided credentials and discover
    #
    # 1. The principal URL
    # 2  The calendar home URL
    #
    # These URL's vary from user to user
    # once doscivered, these  can then be used to manage calendars

    def discover(self):
        # Build and dispatch a request to discover the prncipal us for the
        # given credentials
        headers = {
            'Depth': '1',
        }
        auth = HTTPBasicAuth(self.username, self.password)
        principal_response = requests.request(
            'PROPFIND',
            self.icloud_url,
            auth=auth,
            headers=headers,
            data=self.propfind_principal.encode('utf-8')
        )
        if principal_response.status_code != 207:
            print('Failed to retrieve Principal: ',
                  principal_response.status_code)
            exit(-1)
        # Parse the resulting XML response
        soup = BeautifulSoup(principal_response.content, 'lxml')
        self.principal_path = soup.find(
            'current-user-principal'
        ).find('href').get_text()
        discovery_url = self.icloud_url + self.principal_path
        # Next use the discovery URL to get more detailed properties - such as
        # the calendar-home-set
        home_set_response = requests.request(
            'PROPFIND',
            discovery_url,
            auth=auth,
            headers=headers,
            data=self.propfind_calendar_home_set.encode('utf-8')
        )
        if home_set_response.status_code != 207:
            print('Failed to retrieve calendar-home-set',
                  home_set_response.status_code)
            exit(-1)
        # And then extract the calendar-home-set URL
        soup = BeautifulSoup(home_set_response.content, 'lxml')
        self.calendar_home_set_url = 'http://cal.trumind.net:8008'+soup.find(
            'href',
            attrs={'xmlns':'DAV:'}
        ).get_text()

    # get_calendars
    # Having discovered the calendar-home-set url
    # we can create a local object to control calendars (thin wrapper around
    # CALDAV library)
    def get_calendars(self):
        self.caldav = caldav.DAVClient(self.calendar_home_set_url,
                                       username=self.username,
                                       password=self.password)
        self.principal = self.caldav.principal()
        self.calendars = self.principal.calendars()

    def get_named_calendar(self, name):

        if len(self.calendars) > 0:
            for calendar in self.calendars:
                properties = calendar.get_properties([dav.DisplayName(), ])
                display_name = properties['{DAV:}displayname']
                if display_name == name:
                    return calendar
        return None

    def create_calendar(self,name):
        return self.principal.make_calendar(name=name)

    def delete_all_events(self,calendar):
        for event in calendar.events():
            event.delete()
        return True

    def create_events_from_ical(self, ical):
        # to do
        pass

    def create_simple_timed_event(self,start_datetime, end_datetime, summary,
                                  description):
        # to do
        pass

    def create_simple_dated_event(self,start_datetime, end_datetime, summary,
                                  description):
        # to do
        pass


vcal = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:{}
DTSTAMP:20180104T111016Z
DTSTART:{}
DTEND:{}
SUMMARY:{}
END:VEVENT
END:VCALENDAR
"""

# deep thought
deepThought = ChatBot("Training demo")
deepThought.set_trainer(ListTrainer)
deepThought.train("chatterbot.corpus.chinese")

# time NLP
tn = TimeNormalizer()
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d %H:%M:%S")

uuid = 0

username = 'user01'
password = 'user01'

icx = iCloudConnector(username, password)

cal = icx.get_named_calendar('MyCalendar')

def onQQMessage(bot, contact, member, content):
	global uuid, cal

	if contact.ctype == "buddy":
		res = tn.parse(target = content, timeBase = now)
		res = eval(res)
		if res.has_key('error'):
			bot.SendTo(contact, str(deepThought.get_response(content)))
		else:
			typ = res['type']
			if typ == 'timespan':
				timeArray = time.strptime(res['timespan'][0], "%Y-%m-%d %H:%M:%S")
                                startTime = time.strftime("2018%m%dT%H%M%SZ", timeArray)
				timeArray = time.strptime(res['timespan'][1], "%Y-%m-%d %H:%M:%S")
                                endTime = time.strftime("2018%m%dT%H%M%SZ", timeArray)
				add_event = vcal.format(uuid, startTime, endTime, content)
				try:
					cal.add_event(add_event)
					print(add_event)
				except AuthorisationError as ae:
					print('Couldn\'t add event', ae.reason)
				ansString = str(deepThought.get_response(content))
				if ansString == None:
					ansString = '我再想想'
				bot.SendTo(contact, ansString)
			if typ == 'timestamp':
				timeArray = time.strptime(res['timestamp'], "%Y-%m-%d %H:%M:%S")
				otherStyleTime = time.strftime("2018%m%dT%H%M%SZ", timeArray)
				add_event = vcal.format(uuid, otherStyleTime, otherStyleTime, content)	
				try:
					cal.add_event(add_event)
					print(add_event)
				except AuthorisationError as ae:
					print('Couldn\'t add event', ae.reason)
				ansString = str(deepThought.get_response(content))
				if ansString == None:
					ansString = '我再想想'
				bot.SendTo(contact, ansString)

			if typ == 'timedelta':
				bot.SendTo(contact,str(deepThought.get_response(content)))
	
	uuid += 1
