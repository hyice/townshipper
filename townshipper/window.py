#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyautogui

screen_width, screen_height = pyautogui.size()
image_width, image_height = pyautogui.screenshot().size

screen_scale = image_width / screen_width


def _locations_by_image(image_path):
    locations_iter = pyautogui.locateAllOnScreen(image_path)

    return [(location[0]/screen_scale, location[1]/screen_scale) for location in locations_iter]

def _location_for_image(image_path, try_times=10, confidence=0.8, **kwargs):
    left_try_times = try_times
    while left_try_times:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, **kwargs)

        if location:
            return (location[0]/screen_scale, location[1]/screen_scale)

        left_try_times -= 1

    return None

def _activate_window():
    window_title_position = _location_for_image('resource/settings/window_title.png', confidence=0.95)
    if not window_title_position:
        print('Failed To Activate Window!')
        return False

    pyautogui.click(window_title_position[0], window_title_position[1])
    return True

def full_screen():
    if not _activate_window():
        return False

    left_try_time = 3
    while left_try_time:
        pyautogui.press('esc')
        button_position =_location_for_image('resource/settings/full_screen.png')

        if button_position:
            pyautogui.click(button_position[0], button_position[1])
            pyautogui.press('esc')
            return

    return False

