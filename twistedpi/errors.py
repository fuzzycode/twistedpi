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
Error module
"""

from twisted.python import log


class ErrorCodes(object):
    BAD_REQUEST = 1
    INVALID_COMMAND = 2
    BAD_DATA = 3
    SERVER_ERROR = 4
    INVALID_CAMERA_ARGUMENT = 5

class TwistedPiException(Exception):
    def __init__(self, _msg, _code):
        log.err('{0}({1})'.format(_msg, _code))

        self.msg = _msg
        seld.code = _code

class TwistedPiMethodNotFound(TwistedPiException):
    def __init__(self, _msg, _code, _name):
        super(TwistedPiMethodNotFound, self).__init__(_msg, _code)
        self.name = _name


class TwistedPiValueError(TwistedPiException, ValueError):
    def __init__(self, _msg, _code):
        super(TwistedPiValueError, self).__init__(_msg, _code)
