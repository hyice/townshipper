#!/usr/bin/env python
# -*- coding: utf-8 -*-

import window

window.full_screen()

# barn.open_barn()

# import pyautogui
#
# screen_width, screen_height = pyautogui.size()
# image_width, image_height = pyautogui.screenshot().size
#
# screen_scale = image_width / screen_width
#
# def get_wheat_field_position():
#     pos = pyautogui.locateCenterOnScreen('resource/wheat1.png', confidence=0.8)
#
#     if pos is None:
#         pos = pyautogui.locateCenterOnScreen('resource/wheat2.png', confidence=0.8)
#
#     return (pos[0]/screen_scale, pos[1]/screen_scale) if pos else None
#
#
# wheat_position = None
# while True:
#     wheat_position = get_wheat_field_position()
#
#     if wheat_position:
#         print('found wheat filed, ', wheat_position)
#         pyautogui.moveTo(wheat_position[0], wheat_position[1])
#         continue
#
#     print('not found wheat field')






