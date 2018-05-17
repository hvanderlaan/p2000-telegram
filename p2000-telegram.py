#!/usr/bin/env python

# File   : ./p2000-telegram.py
# Purpose: Python script for showing emergency services pager messages and
#          send them via telegram
#
# Auhtor : Harald van der Laan
# Date   : 2018/05/17
# Version: v1.0.0
#
# Requirements:
#  - requests
#  - bs4
#  - difflib
#  - working internet connection
#
# Changelog:
#  - v1.0.0  initial commit of the script                                 Harald
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

""" p2000.py - display the dutch digital emergency services pager system
    usage   : ./p2000.py --help
    requires: internet connection to download messages from http://p2000mobiel.nl """

from __future__ import (print_function, unicode_literals)

import sys
import os
import re
import ConfigParser
import difflib

try:
    from functions import p2000
except ImportError:
    sys.stderr.write('[-] could not find libp2000.\n')
    sys.exit(1)

def main(conf):
    """ main function """
    args = p2000.get_args()

    token = conf.get('telegram', 'token')
    chatid = conf.get('telegram', 'chatid')

    numlines = args.lines
    url = conf.get('global', 'baseurl') + conf.get('regions', 'region' + args.region)

    data = p2000.get_p2000_data(url)
    p2000data = p2000.convert_to_json(data)

    newfile = os.path.dirname(os.path.abspath(__file__)) + '/p2000.new'
    oldfile = os.path.dirname(os.path.abspath(__file__)) + '/p2000.old'
    difffile = os.path.dirname(os.path.abspath(__file__)) + '/p2000.diff'

    counter = 0
    msg = ''

    p2000.create_files(newfile, oldfile, difffile)

    with open(newfile, 'w') as fdn:
        for _ in range(int(numlines)):
            fdn.write(p2000.p2000_pp(p2000data['p2000'][_]))
            fdn.write('-----\n')

    with open(oldfile, 'r') as fdo, open(newfile, 'r') as fdn:
        diff = diff = difflib.ndiff(fdo.readlines(), fdn.readlines())

    delta = '' .join(x[2:] for x in diff if  x.startswith('+ ') or x.startswith('-----'))

    with open(difffile, 'w') as fdd:
        fdd.write(delta)

    with open(oldfile, 'w') as fdo, open(newfile, 'r') as  fdn:
        fdo.write(fdn.read())

    with open(difffile, 'r') as fdd:
        content = fdd.readlines()

    for _, value in enumerate(content):
        if re.match('^----.*', str(value)):
            value = ''

        if re.match('.*, [012][0123456789]:.*', str(value)):
            if re.match('.*[Aa]mbu.*', str(value)):
                icon = u'\U0001F691'
            elif re.match('.*[Bb]rand.*', str(value)):
                icon = u'\U0001F692'
            elif re.match('.*[Ll]ife.*', str(value)):
                icon = u'\U0001F681'
            else:
                icon = u'\U0001F693'

            value = '{} {}' .format(icon, value)
            counter += 1

        msg = msg + value

    if not args.telegram:
        print(msg)
    else:
        if counter > 0:
            p2000.send_telegram(token, chatid, msg)


if __name__ == "__main__":
    CONFIG = os.path.dirname(os.path.abspath(__file__)) + '/p2000.cfg'
    CONF = ConfigParser.ConfigParser()
    CONF.read(CONFIG)

    main(CONF)

    sys.exit(0)
