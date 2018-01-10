#!/usr/bin/env python
# -*- coding:utf-8 -*-

#
# This file defines a class that eases the connection to iCload for caldav manipulation
# Is uses the credentials supplied in the constructor to discver the users principal and calendar-home-set urls then uses
# these as inputs to the CALDAV library to add a caledndar, and create an event
# If the example is re-run - an Authorisation error will occur as the example will try to re-add the same event which will be rejected due to the duplicate ID
#

from __future__ import print_function

from datetime import datetime
import sys

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

# Simple example code

# 格式化时间字串
# DTSTAMP = time.strftime('%Y%m%dT%H%M%SZ', time.localtime())

vcal = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:0000000008
DTSTAMP:20180104T111016Z
DTSTART:20180104T111016Z
DTEND:20180104T131016Z
SUMMARY:This is an event
END:VEVENT
END:VCALENDAR
"""

username = 'user01'
password = 'user01'
# The above is an 'application password' any app must now have its own
# password in iCloud. For info refer to
# https://www.imore.com/how-generate-app-specific-passwords-iphone-ipad-mac

icx = iCloudConnector(username, password)

# 获取所有日历
cal = icx.get_named_calendar('MyCalendar')

# 新建日历
if not cal:
    cal = icx.create_calendar('MyCalendar')

#新建事件
try:
    cal.add_event(vcal)
except AuthorisationError as ae:
    print('Couldn\'t add event', ae.reason)

#获取 2018/1/1 ~ 2018/6/1 间的所有事件
results = cal.date_search(datetime(2018, 1, 1), datetime(2018, 6, 1))
for event in results:
    print("Found", event)
    print(event.data)  # 打印事件的数据
    #event.delete()  //删除服务器上的事件
    print("----------")

