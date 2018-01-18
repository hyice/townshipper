#!/usr/bin/env python
# -*- coding: utf-8 -*-

import state
import messenger
import pyautogui
import time

time.sleep(10)

if not messenger.init():
    exit()

im = pyautogui.screenshot()
messenger._send_mail('[HOME] ALL ACTIONS', '', im)


# print(state.current_state)
#
# state.current_state[0]()
#
# print(state.current_state)
#
# state.current_state[2]()
#
# print(state.current_state)






