#!/usr/bin/env python
# -*- coding: utf-8 -*-

import messenger
import commander
import game
import time

# if not messenger.init():
#     exit()
#
# commander.check_and_handle_new_command()

def auto_planting():
    # time.sleep(5)

    plant = 'wheat'
    while True:

        while game.Field.plant(plant):
            pass

        while True:
            try:
                result = game.Field.harvest(plant, plant_new=True)
            except game.BarnIsFull:
                game.Barn.sell(plant, -2)
            else:
                if not result:
                    break

if __name__ == '__main__':
    try:
        # time.sleep(10)
        # window._all_locations_for_image('resource/field/wheat.png', confidence=0.8)
        auto_planting()
    except KeyboardInterrupt:
        exit(0)
