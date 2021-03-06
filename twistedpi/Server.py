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
Server module
"""


#Twisted modules
from twisted.internet.protocol import Factory
from twisted.internet import threads
from twisted.python import log
from twisted.protocols.basic import NetstringReceiver
from twisted.internet.defer import succeed, maybeDeferred

import json
import base64
import logging
import types

#Camera modules
import Camera

#twistedpi modules
from errors import (ErrorCodes, TwistedPiException, TwistedPiMethodNotFound,
                    TwistedPiValueError)
from twistedpi import __VERSION__, __NAME__


__logger = logging.getLogger(__name__)

VERBOSE = 5


def DecodeRequest(_request):
    """

    :param _request:
    :return: :raise TwistedPiValueError:
    """
    log.msg('Decoding request')

    try:
        return json.loads(_request)
    except ValueError as _e:
        log.err(_e)
        raise TwistedPiValueError('Inavalid JSON', ErrorCodes.BAD_DATA)
    except Exception as _e:
        log.err(_e)
        raise


def EncodeResult(_result):
    """

    :param _result:
    :return: :raise TwistedPiValueError:
    """
    try:
        return json.dumps(_result)
    except ValueError as _e:
        log.err(_e)
        raise TwistedPiValueError('Invalid JSON', ErrorCodes.BAD_DATA)


def ValidateRequest(_request):
    """

    :param _request:
    :return: :raise TwistedPiValueError:
    """
    log.msg('Validating Request')

    if not 'command' in _request or not isinstance (_request['command'], types.StringTypes):
        raise TwistedPiValueError('Missing command', ErrorCodes.BAD_REQUEST)

    return _request


def PrepareRequest(_request):
    """

    :param _request:
    :return: :raise:
    """
    log.msg('Preparing Request {0}'.format(_request))

    try:
        _request['command'] = _request['command'].upper()
    except Exception as _e:
        log.err(_e)
        raise

    if not 'args' in _request:
        _request['args'] = dict()

    return _request


def ResponseSuccess(_result, **kwargs):
    """

    :param _result:
    :param kwargs:
    :return:
    """
    response = dict([('command', kwargs['command'])])
    response['payload'] = _result

    return response


def ResponseFail(_fail, **kwargs):
    """

    :param _fail:
    :param kwargs:
    :return:
    """
    _fail.trap(TwistedPiException)

    response = dict([('command', kwargs['command'])])
    response['error'] = dict()

    _error = _fail.value
    response['error']['code'] = _error.code

    return response


def EncodeData(_data):
    """

    :param _data:
    :return:
    """
    _data = base64.b64encode(_data)
    log.msg('Encoded Length: {0}'.format(len(_data)))

    return _data


def LogServerFailure(_failure):
    """

    :param _failure:
    """
    log.err(_failure)


class JSONCommandProtocol(NetstringReceiver):
    """

    :param _factory:
    """

    def __init__(self, _factory):
        self.factory = _factory

    def connectionMade(self):
        """

        :return:
        """
        log.msg('Connection opened')
        self.factory.connectionMade()

        #Send server information to client
        d = succeed(dict([('version', __VERSION__), ('name', __NAME__)]))
        d.addCallbacks(self._finalizeRequest, LogServerFailure)
        return d

    def connectionLost(self, _reason):
        """

        :param _reason:
        """
        log.msg('Connection lost: {0}'.format(_reason))
        self.factory.connectionLost()

    def _handleCommand(self, _request):
        command = _request['command']
        function = getattr(self, 'handle_{0}'.format(command), None)

        if callable(function):
            return  maybeDeferred(function, _request['args'])
        else:
            log.msg('No command found')
            msg = 'Invalid command {0}'.format(command)
            raise TwistedPiMethodNotFound(msg, ErrorCodes.INVALID_COMMAND)

    def _sendResponse(self, _response):
        log.msg('Sending Response. Size {0}'.format(len(_response)))
        #log.msg('<--- {0}'.format(_response), logLevel=VERBOSE)
        self.sendString(_response)

    def _finalizeRequest(self, _result):
        result = EncodeResult(_result)
        self._sendResponse(result)

    def stringReceived(self, _line):
        log.msg('---> {0}'.format(_line), logLevel=logging.DEBUG)

        try:
            request = DecodeRequest(_line)
        except TwistedPiValueError as e:
            log.err(e)
        else:
            log.msg(request)
            #Prepare incoming request
            d = succeed(request)
            d.addCallback(ValidateRequest)
            d.addCallback(PrepareRequest)

            #Handle request
            d.addCallback(self._handleCommand)

            #Prepare and handle result
            d.addCallbacks(ResponseSuccess, ResponseFail,
                           callbackKeywords=request, errbackKeywords=request)
            d.addCallbacks(self._finalizeRequest, LogServerFailure)

            return d


class CameraProtocol(JSONCommandProtocol):
    def handle_PING(self, _args):
        """

        :param _args:
        :return:
        """
        log.msg('handle_PING', logLevel=logging.DEBUG)
        return 'PONG'

    def handle_IMAGE(self, _args):
        """

        :param _args:
        :return: :raise TwistedPiException:
        """
        log.msg('handle_image', logLevel=logging.DEBUG)

        def imageSuccess(_image):
            assert _image is not None, "Image is None"

            log.msg('Image Size: {0} bytes'.format(_image.tell())
                    ,logLevel = logging.DEBUG)

            _image.seek(0)
            return threads.deferToThread(EncodeData, _image.read())

        def imageError(_err):
            log.err(_err)
            raise TwistedPiException("Error capturing Image",
                                     ErrorCodes.SERVER_ERROR)

        _args = Camera.validate_image_args(_args)

        d = threads.deferToThread(Camera.take_image, _args)
        d.addCallbacks(imageSuccess, imageError)

        return d


class ImageServerFactory(Factory):
    def __init__(self, _config):
        log.msg('Creating Protocol Factory', logLevel=logging.DEBUG)

    def doStart(self):
        """
        TODO
        """
        log.msg('Factory.doStart...', logLevel=logging.DEBUG)

    def doStop(self):
        """
        TODO
        """
        log.msg('Factory.doStop...', logLevel=logging.DEBUG)

    def startConnecting(self, _connectorInstance):
        """

        :param _connectorInstance:
        """
        log.msg('Start Connecting: {0}'.format(_connectorInstance),
                logLevel=logger.DEBUG)

    def clientConnectionLost(self, _connection, _reason):
        """

        :param _connection:
        :param _reason:
        """
        log.msg('{0} connection lost {1}'.format(_connection, _reason))


    def buildProtocol(self, _addr):
        """

        :param _addr:
        :return:
        """
        log.msg('Creating Protocol for {0}'.format(_addr),
                logLevel=logging.DEBUG)

        return CameraProtocol(self)

    def stopFactory(self):
        """
        TODO
        """
        log.msg('Stopping Protocol Factory', logLevel=logging.DEBUG)

    def connectionMade(self):
        """
        TODO
        """
        pass

    def connectionLost(self):
        """
        TODO
        """
        pass
