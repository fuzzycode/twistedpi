# -*- coding: utf-8 -*-

# Copyright (C) 2014 Björn Larsson

# This file is part of twistedpi.
#
# twistedpi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# twistedpi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with twistedpi.  If not, see <http://www.gnu.org/licenses/>.

"""
A Twisted plugin to allow remote control of the Raspberry Pi
camera module.
"""
from setuptools import setup, find_packages

from twistedpi import __VERSION__, __NAME__


try:
    import twisted
    import picamera
except ImportError:
    raise SystemExit('Required packages not found')

__author__ = 'Björn Larsson'
__author_mail__ = 'develop@bjornlarsson.net'
__url__ = 'https://github.com/fuzzycode/twistedpi'

__platforms__ = []

__keywords__ = [
    'raspberry pi',
    'camera',
    'twisted',
    'remote control'
]

__classifiers__ = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Programming Language :: Python',
    'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
    'Topic :: System :: Networking',
]

__requires__ = [
    'twisted',
    'picamera'
]

__packages__ = []

__entry_points__ = {}


def get_description():
    try:
        return open("README.rst").read() + '\n' + open("CHANGES.txt").read()
    except Exception:
        return "No description"


setup(
    name=__NAME__,
    author=__author__,
    author_email=__author_mail__,
    version='.'.join([str(s) for s in __VERSION__]),
    description=__doc__,
    url=__url__,

    long_description=get_description(),

    license='LGPLv3',
    keywords=' '.join(__keywords__),
    packages=find_packages(),

    classifiers=__classifiers__,
    platforms=__platforms__,
    install_requires=__requires__,
    entry_points=__entry_points__,
)




# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))
