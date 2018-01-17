#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyautogui
import location
import time

_images = {
    'house': 'resource/barn/house.png',
}


def open_barn():
    i = 0
    while i < 10:
        print(location.locations_by_image(_images['house']))
        i += 1
