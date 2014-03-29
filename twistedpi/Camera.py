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
from twisted.python import log


import threading
import logging
import io

import picamera

from errors import ErrorCodes, TwistedPiValueError


__lock = threading.Lock()
__log = logging.getLogger(__name__)


def ValidateImageArgs(_args):
    if not 'format' in _args:
        _args['format'] = 'jpeg' #Default to jpeg if format is missing

    return _args


def TakeImage(_args):
    with __lock:
        with picamera.PiCamera() as camera:
            stream = io.BytesIO()

            #Configure Camera
            try:
                if 'resolution' in _args:
                    camera.resolution = (_args['resolution'][0],
                                         _args['resolution'][1])


            except picamera.exc.PiCameraValueError as e:
                raise TwistedPiValueError('Invalid Camera Arguments',
                                          ErrorCodes.INVALID_CAMERA_ARGUMENT)

            except:
                raise TwistedPiValueError('Invalid Camera Arguments',
                                          ErrorCodes.INVALID_CAMERA_ARGUMENT)

            #Capture frame
            try:
                camera.capture(stream, format=_args['format'])
            except picamera.exc.PiCameraValueError as e:
                raise TwistedPiValueError('Bad Camera Argument',
                                          ErrorCodes.INVALID_CAMERA_ARGUMENT)
            except:
                raise TwistedPiException('Error Capturing Image',
                                         ErrorCodes.SERVER_ERROR)
            else:
                return stream
