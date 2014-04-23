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
Camera module
"""

from twisted.python import log

import threading
import logging
import io

import picamera

from errors import ErrorCodes, TwistedPiValueError, TwistedPiException


__lock = threading.Lock()
__log = logging.getLogger(__name__)


def validate_image_args(_args):
    """
    Validate the camera arguments. Ensures that a camera format is provided.

    :param _args:
    :return: A dictionary of validated arguments
    """
    if not 'format' in _args:
        _args['format'] = 'jpeg'  # Default to jpeg if format is missing

    return _args


def take_image(_args):
    """
    Capture an image using the provided arguments.

    :param _args:
    :return:
    :raise TwistedPiException:
    """
    with __lock:
        with picamera.PiCamera() as camera:
            stream = io.BytesIO()

            #Configure Camera
            try:
                if 'resolution' in _args:
                    camera.resolution = (_args['resolution'][0],
                                         _args['resolution'][1])
                if 'ISO' in _args:
                    camera.ISO = _args['ISO']
                if 'awb_mode' in _args:
                    camera.awb_mode = _args['awb_mode']
                if 'brightness' in _args:
                    camera.brightness = _args['brightness']
                if 'color_effects' in _args:
                    camera.color_effects = _args['color_effects']
                if 'contrast' in _args:
                    camera.contrast = _args['contrast']
                if 'crop' in _args:
                    camera.crop = _args['crop']
                if 'exif_tags' in _args:
                    for k, v in _args['exif_tags']:
                        camera.exif_tags[k] = v
                if 'exposure_compensation' in _args:
                    camera.exposure_compensation = _args['exposure_compensation']
                if 'exposure_mode' in _args:
                    camera.exposure_mode = _args['exposure_mode']
                if 'hflip' in _args:
                    camera.hflip = _args['hflip']
                if 'led' in _args:
                    camera.led = _args['led']
                if 'meter_mode' in _args:
                    camera.meter_mode = _args['meter_mode']
                if 'rotation' in _args:
                    camera.rotation = _args['rotation']
                if 'saturation' in _args:
                    camera.rotation = _args['saturation']
                if 'sharpness' in _args:
                    camera.sharpness = _args['sharpness']
                if 'shutter_speed' in _args:
                    camera.shutter_speed = _args['shutter_speed']
                if 'vflip' in _args:
                    camera.vflip = _args['vflip']

            except picamera.PiCameraValueError as e:
                raise TwistedPiValueError('Invalid Camera Arguments',
                                          ErrorCodes.INVALID_CAMERA_ARGUMENT)

            #Capture frame
            try:
                format = _args.get('format', 'jpeg')
                resize = _args.get('resize', None)

                options = dict()
                if format == 'jpeg':
                    options['quality'] = _args.get('quality', 85)
                    options['thumbnail'] = _args.get('thumbnail', None)

                camera.capture(stream, format=format, use_video_port=False,
                               resize=resize, **options)

            except picamera.PiCameraValueError as e:
                raise TwistedPiValueError('Bad Camera Argument',
                                          ErrorCodes.INVALID_CAMERA_ARGUMENT)
            else:
                #Save all camera settings
                settings = dict([
                    ('resolution', camera.resolution),
                    ('ISO', camera.ISO),
                    ('awb_mode', camera.awb_mode),
                    ('brightness', camera.brightness),
                    ('color_effects', camera.color_effects),
                    ('contrast', camera.contrast),
                    ('crop', camera.crop),
                    ('exif_tags', camera.exif_tags),
                    ('exposure_compensation', camera.exposure_compensation),
                    ('exposure_mode', camera.exposure_mode),
                    ('hflip', camera.hflip),
                    ('led', camera.led),
                    ('meter_mode', camera.meter_mode),
                    ('rotation', camera.rotation),
                    ('saturation', camera.saturation),
                    ('sharpness', camera.sharpness),
                    ('shutter_speed', camera.shutter_speed),
                    ('vflip', camera.vflip)])

                settings['format'] = format
                settings['resize'] = resize

                if format == 'jpeg':
                    settings['quality'] = options['quality']
                    settings['thumbnail'] = options['thumbnail']

                return stream
