#!/usr/bin/env python

# File   : ./functions/p2000.py
# Purpose: Library file for the p2000.py script
#
# Auhtor : Harald van der Laan
# Date   : 2018/5/17
# Version: v1.0.2
#
# Requirements:
#  - requests
#  - bs4
#  - working internet connection
#
# Changelog:
#  - v1.0.1     Created new header in python files                       Harald
#  - v1.0.0     Initial version                                          Harald
#
# Copyright:
# =============================================================================
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For the full license, see the LICENSE file.
#
# Disclaimer:
# =============================================================================
# Software provided by Harald van der Laan is for illustrative purposes only
# which provides customers with programming information regarding the products.
# This software is supplied "AS IS" without any warranties and support.
#
# Harald van der Laan assumes no responsibility or liability for the use of the
# software, conveys no license or title under any patent, copyright, or mask
# work right to the product.
#
# Harald van der Laan reserves the right to make changes in the software without
# notification. Harald van der Laan also make no representation or warranty that
# such application will be suitable for the specified use without further
# testing or modification.

""" libp2000/p2000functions.py -  functions file for p2000 notifications """

import sys
import os
import re
import datetime
import argparse

import bs4
import requests

try:
    import json
except ImportError:
    import simplejson as json

def get_args():
    """ getting the arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lines', help='number of lines', default='5')
    parser.add_argument('-r', '--region', help='security region', default='40')
    parser.add_argument('-t', '--telegram', help='send notifications with telegram',
                        default=False, action='store_true')

    return parser.parse_args()

def get_p2000_data(url):
    """ function to get p2000 data from the internet.
    this function requires: requests and bs4.BeautifulSoup """

    try:
        html = requests.get(url)
    except requests.exceptions.ConnectionError:
        sys.stderr.write('[-] connection failed.\n')
        sys.exit(1)

    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    data = soup.findAll('div', {'class': ['date', 'message', 'called',
                                          'call_type_1', 'call_type_2', 'call_type_3',
                                          'call_type_4', 'call_type_5', 'call_type_6',
                                          'call_type_7', 'call_type_8', 'call_type_9']})

    return data

def convert_to_json(data):
    """ function to convert data to json formatted data.
        this dunction requires: re and json """

    now = str(datetime.datetime.now().strftime("%a %d %B %Y, "))
    jsondata = '{"p2000": ['

    # matching all relevant lines.
    for line in data:
        if re.match('.*\"date', str(line)):
            line = '{"date": "' + now + str(line) + '", '
        if re.match('.*\"call_type_', str(line)):
            line = '"call_type": "' + str(line) + '", '
        if re.match('.*\"message', str(line)):
            line = '"message": "' + str(line) + '", '
        if re.match('.*\"called', str(line)):
            line = '"called": ["' + str(line) + '"]},'

        # substitute <br/> to , for valid json format
        line = re.sub('<br/>', '", "', str(line))
        # remove other html taggs
        line = re.sub('<[^>]+>', '', str(line))

        jsondata = jsondata + line

    # create valid json closing
    jsondata = jsondata[:-1] + ']}'

    return json.loads(jsondata)

def p2000_pp(msg):
    """ p2000 post processing """
    regex = '.*[Zz][Ee][Vv].*|.*[Zz][Vv].*|.*690[0-9].*|^[Pp] 1|.*[Pp]rio.*|'
    regex += '.*[Aa]12.*|.*[Aa]50.*|.*[Aa]15.*|.*[AaNn]325.*'

    if re.match(regex, str(msg["message"])):
        ret = '{} - {}\n'.format(msg["date"], msg["call_type"])
        ret += '<strong>{}</strong>\n'.format(msg["message"])
        for i in xrange(len(msg['called'])):
            ret += '{}\n' .format(msg['called'][i])
    elif re.match('.*Lifeliner.*', str(msg["call_type"])):
        ret = '{} - {}\n'.format(msg["date"], msg["call_type"])
        ret += '<strong>{}</strong>\n'.format(msg["message"])
        for i in xrange(len(msg['called'])):
            ret += '{}\n' .format(msg['called'][i])
    else:
        ret = ''

    return ret

def send_telegram(token, chatid, data):
    """ send notification to telegram """
    url = 'https://api.telegram.org/bot' + token + '/sendMessage'
    content = {'chat_id': chatid, 'text': data.encode('utf-8'), 'parse_mode': 'html'}

    return requests.post(url, data=content)

def create_files(newfile, oldfile, difffile):
    """ function for creating files that are needed to see if notifications are new """
    if not os.path.exists(newfile):
        with open(newfile, 'w') as fdn:
            fdn.write('')

    if not os.path.exists(oldfile):
        with open(oldfile, 'w') as fdo:
            fdo.write('')

    if not os.path.exists(difffile):
        with open(difffile, 'w') as fdd:
            fdd.write('')
