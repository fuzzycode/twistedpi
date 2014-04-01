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

#Zope modules
from zope.interface import implements

#Twisted modules
from twisted.python import usage
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from twisted.application import internet
from twisted.python import log


#std modules
import logging

#twistedpi modules
from twistedpi import Server

__logger = logging.getLogger(__name__)


class Options(usage.Options):
    optParameters = [
        ["port", "p", 8090, "Server port number"]]


    def opt_Version(self):
        """
        Display twistedpi version and exit.
        """
        from twistedpi import __VERSION__
        print("twistedpi version: {0}.{1}.{2}".format(*__VERSION__))
        raise SystemExit(0)

class ServiceMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = "twistedpi"
    description = "Service to remote control the Raspberry Pi camera module"
    options = Options

    def makeService(self, _config):
        #observer = log.PythonLoggingObserver()
        #observer.start()


        factory = Server.ImageServerFactory(_config)
        return internet.TCPServer(int(_config["port"]), factory)


serviceMaker = ServiceMaker()
