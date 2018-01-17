#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyautogui

screen_width, screen_height = pyautogui.size()
image_width, image_height = pyautogui.screenshot().size

screen_scale = image_width / screen_width


def locations_by_image(image_path):
    locations_iter = pyautogui.locateAllOnScreen(image_path)

    return [(location[0]/screen_scale, location[1]/screen_scale) for location in locations_iter]
