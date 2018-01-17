#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyautogui

screen_width, screen_height = pyautogui.size()
image_width, image_height = pyautogui.screenshot().size

screen_scale = image_width / screen_width


def _locations_by_image(image_path):
    locations_iter = pyautogui.locateAllOnScreen(image_path)

    return [(location[0]/screen_scale, location[1]/screen_scale) for location in locations_iter]


def _location_for_image(image_path, try_times=10, confidence=0.95, **kwargs):
    left_try_times = try_times
    while left_try_times:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, **kwargs)

        if location:
            return location[0]/screen_scale, location[1]/screen_scale

        left_try_times -= 1

    return None


def _activate_window():
    window_title_position = _location_for_image('resource/settings/window_title.png')
    if not window_title_position:
        return False

    pyautogui.click(window_title_position[0], window_title_position[1])
    return True


def full_screen():
    if not _activate_window():
        return False

    left_try_time = 3
    while left_try_time:
        pyautogui.press('esc')
        button_position = _location_for_image('resource/settings/full_screen.png', try_times=3)

        if button_position:
            pyautogui.click(button_position[0], button_position[1])
            pyautogui.press('esc')
            return True

    return False


class Barn:
    RESOURCE_BASE_DIR = 'resource/barn/'

    all_items = [
        'glass', 'brick', 'slab', 'paint', 'hammer', 'nail',  # building materials
        'wheat', 'corn', 'carrot', 'sugarcane', 'cotton',  # field plant's
        'milk',  # animal's
    ]

    @classmethod
    def open(cls):
        return cls._find_and_click_image('house.png')

    @classmethod
    def upgrade(cls):
        return cls._find_and_click_image('upgrade.png')

    @classmethod
    def detail_for_item(cls, item):
        if item not in cls.all_items:
            return False

        return cls._find_and_click_image(item + '.png')

    @classmethod
    def increase_sell_amount(cls):
        return cls._find_and_click_image('increase.png')

    @classmethod
    def decrease_sell_amount(cls):
        return cls._find_and_click_image('decrease.png')

    @classmethod
    def sell(cls):
        return cls._find_and_click_image('sell.png')

    @classmethod
    def _find_and_click_image(cls, image_name):
        position = _location_for_image(cls.RESOURCE_BASE_DIR + image_name)

        if not position:
            return False

        pyautogui.click(position[0], position[1])
        return True

