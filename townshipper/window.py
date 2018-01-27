#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyautogui
import logging
import time


def _logger():
    logger = logging.getLogger('window')
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def _screen_scale():
    screen_width, screen_height = pyautogui.size()
    image_width, image_height = pyautogui.screenshot().size

    return image_width / screen_width


_latest_founded_regions = {}


def _location_for_image_in_latest_region(image_path, confidence, **kwargs):
    try:
        search_region = _latest_founded_regions[image_path]
    except KeyError:
        return None
    else:
        search_region = (search_region[0] - 100, search_region[1] - 100, search_region[2] + 200, search_region[3] + 200)
        logger.debug('try to find location for {0} by latest region {1}'.format(image_path, search_region))

        region = pyautogui.locateOnScreen(image_path, confidence=confidence, region=search_region, **kwargs)
        if not region:
            return None

        center_x, center_y = pyautogui.center(region)
        center = (center_x / screen_scale, center_y / screen_scale)
        logger.debug('--> image founded at {0}'.format(center))
        return center


def _location_for_image(image_path, try_times=3, confidence=0.9, cache=False, **kwargs):
    if cache:
        location_by_latest_region = _location_for_image_in_latest_region(image_path, confidence, **kwargs)
        if location_by_latest_region:
            return location_by_latest_region

    left_try_times = try_times
    while left_try_times:
        logger.debug('start to find location for image {0} with confidence {1}'.format(image_path, confidence))
        region = pyautogui.locateOnScreen(image_path, confidence=confidence, **kwargs)

        if region:
            center_x, center_y = pyautogui.center(region)
            center = (center_x / screen_scale, center_y / screen_scale)
            logger.debug('--> image founded at {0}'.format(center))
            if cache:
                _latest_founded_regions[image_path] = region
            return center

        left_try_times -= 1

    logger.debug('--> failed to find location for image')
    return None


def _all_locations_for_image(image_path, confidence=0.9, **kwargs):
    logger.debug('start to find all locations for image {0} with confidence {1}'.format(image_path, confidence))

    pre_x = None
    pre_y = None
    for x, y, width, height in pyautogui.locateAllOnScreen(image_path, confidence=confidence, **kwargs):
        center_x = (x + width / 2.0) /screen_scale
        center_y = (y + height / 2.0) / screen_scale

        logger.debug('--> find location: {0}'.format((center_x, center_y)))

        if pre_x and abs(center_x - pre_x) < (width / 3.0) and abs(center_y - pre_y) < (height / 3.0):
            logger.debug('----> this location is similar to the one before, so just filtered')
            continue

        pre_x, pre_y = center_x, center_y
        yield center_x, center_y


def _find_and_click_image(image_path, **kwargs):
    location = _location_for_image(image_path, **kwargs)

    if not location:
        return False

    x, y = location
    pyautogui.click(x, y)
    return True


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
        button_position = _location_for_image('resource/settings/full_screen.png')

        if button_position:
            pyautogui.click(button_position[0], button_position[1])
            pyautogui.press('esc')
            return True

    return False


def screenshot():
    return pyautogui.screenshot()


class Window():
    @classmethod
    def home(cls):
        logger.debug('start return to home window')
        detect_depth = 5
        while detect_depth:
            logger.debug('start detecting exit full screen icon')
            exit_full_screen_icon = _location_for_image(cls._path_for_image('exit_full_screen'))
            pyautogui.press('esc')

            if exit_full_screen_icon:
                logger.debug('exit full screen icon detected, already returned to home window')
                return True

            logger.debug('exit full screen icon not found, go back to parent window')
            pyautogui.press('esc')

            detect_depth -= 1

        logger.debug('failed to return to home window')
        return False

    @classmethod
    def barn(cls):
        if not cls.home():
            logger.debug("can't open barn window when failed to return to home window")
            return False

        return _find_and_click_image(cls._path_for_image('barn'))

    @classmethod
    def _path_for_image(cls, image_name):
        return 'resource/home/{0}.png'.format(image_name)


class Barn:
    all_items = [
        'glass', 'brick', 'slab', 'paint', 'hammer', 'nail',  # building materials
        'wheat', 'corn', 'carrot', 'sugarcane', 'cotton',  # field plant's
        'milk',  # animal's
    ]

    @classmethod
    def sell(cls, item, amount=-1):
        """
        :param amount: -2 for sell all, -1 for sell half
        """
        logger.debug('start to sell {0} with amount {1}'.format(item, amount))
        if not cls._detail_for_item(item):
            logger.debug('failed to open item detail window')
            return False

        if amount == -2:
            cls._increase_sell_amount(to_maximum=True)
        elif amount == -1:
            pass
        elif amount == 0:
            return True
        else:
            cls._decrease_sell_amount(to_minimal=True)

            for i in range(1, amount):
                if not cls._increase_sell_amount():
                    logger.debug("failed to sell item, can't set to the needed amount")
                    return False

        if not _find_and_click_image(cls._path_for_image('sell')):
            return False

        Window.home()

        return True

    @classmethod
    def _detail_for_item(cls, item):
        if not Window.barn():
            return False

        if item not in cls.all_items:
            return False

        return _find_and_click_image(cls._path_for_image(item))

    @classmethod
    def _increase_sell_amount(cls, to_maximum=False):
        position = _location_for_image(cls._path_for_image('increase'))

        if not position:
            return False

        x, y = position
        if to_maximum:
            pyautogui.mouseDown(x, y)
            time.sleep(5)
            pyautogui.mouseUp()
        else:
            pyautogui.click(x, y)

        return True

    @classmethod
    def _decrease_sell_amount(cls, to_minimal=False):
        position = _location_for_image(cls._path_for_image('decrease'))

        if not position:
            return False

        x, y = position
        if to_minimal:
            while True:
                pyautogui.mouseDown(x, y)
                time.sleep(5)
                pyautogui.mouseUp()
        else:
            pyautogui.click(x, y)

        return True

    @classmethod
    def is_full(cls):
        full_dialog = _location_for_image(cls._path_for_image('full_barn'), try_times=1)
        if full_dialog:
            return True

        return False

    @classmethod
    def _path_for_image(cls, image_name):
        return 'resource/barn/{0}.png'.format(image_name)


class Field:
    RESOURCE_BASE_DIR = 'resource/field/'

    all_items = "wheat,corn,carrot,sugarcane,cotton,strawberry,tomato,pine_tree"

    @classmethod
    def plant(cls, item):
        logger.debug('start to plant {0}'.format(item))
        if not cls._is_valid_plant(item):
            logger.debug('failed to plant, it is not a valid plant')
            return False

        field_position = _location_for_image(cls.RESOURCE_BASE_DIR + 'empty_field.png', confidence=0.85)
        if not field_position:
            logger.debug('failed to plant, there is no empty field')
            return False

        pyautogui.click(field_position[0], field_position[1])

        seed_position = _location_for_image(cls.RESOURCE_BASE_DIR + item + '_seed.png', confidence=0.85, cache=True)
        if not seed_position:
            logger.debug('failed to plant, can not get the seed')
            return False

        pyautogui.moveTo(seed_position[0], seed_position[1])
        pyautogui.dragTo(field_position[0], field_position[1])
        logger.debug('finished planting')
        return True

    @classmethod
    def harvest(cls, item, plant_new=False):
        logger.debug('start to harvest {0}'.format(item))
        if not cls._is_valid_plant(item):
            logger.debug('--> [failed] to harvest, it is not a valid plant')
            return False

        for position in _all_locations_for_image(cls.RESOURCE_BASE_DIR + item + '.png', confidence=0.9):
        # if not position:
        #     logger.debug("--> [failed] to harvest, can't find any {0} to harvest".format(item))
        #     return False

            pyautogui.doubleClick(position[0], position[1], 0.3)

            if Barn.is_full():
                logger.debug('--> [failed] to harvest, because the barn is full')
                raise BarnIsFull

            if plant_new:
                logger.debug('start to plant at harvested place')
                cls._plant_at(item, position)

        return True

    @classmethod
    def _is_valid_plant(cls, item):
        if item not in cls.all_items.split(','):
            print('not valid plant name:', item)
            return False
        return True

    @classmethod
    def _plant_at(cls, item, field_position):
        pyautogui.click(field_position[0], field_position[1])

        seed_position = _location_for_image(cls.RESOURCE_BASE_DIR + item + '_seed.png', confidence=0.85, cache=True)
        if not seed_position:
            return False

        pyautogui.moveTo(seed_position[0], seed_position[1])
        pyautogui.dragTo(field_position[0], field_position[1])
        return True

class BarnIsFull(Exception):
    pass

screen_scale = _screen_scale()
logger = _logger()