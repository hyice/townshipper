#!/usr/bin/env python
# -*- coding: utf-8 -*-

import my_logger
import window


def _activate_window():
    window_title_position = window.locate('resource/settings/window_title.png')
    if not window_title_position:
        return False

    window.click(*window_title_position)
    return True


def full_screen():
    if not _activate_window():
        return False

    return window.locate_and_click('resource/settings/full_screen.png')


class Window():
    @classmethod
    def home(cls):
        logger.debug('start return to home window')
        detect_depth = 5
        while detect_depth:
            logger.debug('start detecting exit full screen icon')
            exit_full_screen_icon = window.locate(cls._path_for_image('exit_full_screen'))
            window.press('esc')

            if exit_full_screen_icon:
                logger.debug('exit full screen icon detected, already returned to home window')
                return True

            logger.debug('exit full screen icon not found, go back to parent window')
            window.press('esc')

            detect_depth -= 1

        logger.debug('failed to return to home window')
        return False

    @classmethod
    def barn(cls):
        if not cls.home():
            logger.debug("can't open barn window when failed to return to home window")
            return False

        return window.locate_and_click(cls._path_for_image('barn'))

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

        if not window.locate_and_click(cls._path_for_image('sell')):
            return False

        Window.home()

        return True

    @classmethod
    def _detail_for_item(cls, item):
        if not Window.barn():
            return False

        if item not in cls.all_items:
            return False

        return window.locate_and_click(cls._path_for_image(item))

    @classmethod
    def _increase_sell_amount(cls, to_maximum=False):
        position = window.locate(cls._path_for_image('increase'))

        if not position:
            return False

        x, y = position
        if to_maximum:
            window.hold(x, y, last_for=5.0)
        else:
            window.click(x, y)

        return True

    @classmethod
    def _decrease_sell_amount(cls, to_minimal=False):
        position = window.locate(cls._path_for_image('decrease'))

        if not position:
            return False

        x, y = position
        if to_minimal:
            while True:
                window.hold(x, y, last_for=5.0)
        else:
            window.click(x, y)

        return True

    @classmethod
    def is_full(cls):
        full_dialog = window.locate(cls._path_for_image('full_barn'), retry_times=1)
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
    def plant(cls, item, positions=None):
        logger.debug('start to plant {0}'.format(item))
        if not cls._is_valid_plant(item):
            logger.error('failed to plant, it is not a valid plant')
            return False

        if not positions:
            all_fields = tuple(window.locate_all(cls.RESOURCE_BASE_DIR + 'empty_field.png', confidence=0.85))
        else:
            all_fields = tuple(positions)

        if len(all_fields) == 0:
            logger.debug('failed to plant, there is no empty field')
            return False

        window.click(*all_fields[0])

        seed_position = window.locate(cls.RESOURCE_BASE_DIR + item + '_seed.png', confidence=0.85)
        if not seed_position:
            logger.error('failed to plant, can not get the seed')
            return False

        window.drag_through((seed_position, *all_fields))
        logger.debug('finished planting')
        return True

    @classmethod
    def harvest(cls, item, plant_new=False):
        logger.debug('start to harvest {0}'.format(item))
        if not cls._is_valid_plant(item):
            logger.error('--> [failed] to harvest, it is not a valid plant')
            return False

        all_ripe_items = tuple(window.locate_all(cls.RESOURCE_BASE_DIR + item + '.png', confidence=0.85))

        if len(all_ripe_items) == 0:
            logger.debug('failed to harvest, there is no ripe item')
            return False

        if len(all_ripe_items) == 1:
            window.double_click(*all_ripe_items[0])
        else:
            window.click(*all_ripe_items[0])
            window.drag_through(all_ripe_items)

        if Barn.is_full():
            logger.debug('--> [failed] to harvest, because the barn is full')
            raise BarnIsFull

        if plant_new:
            logger.debug('start to plant at harvested place')
            cls.plant(item, positions=all_ripe_items)

        return True

    @classmethod
    def _is_valid_plant(cls, item):
        if item not in cls.all_items.split(','):
            print('not valid plant name:', item)
            return False
        return True


class BarnIsFull(Exception):
    pass


logger = my_logger.get_logger('game')