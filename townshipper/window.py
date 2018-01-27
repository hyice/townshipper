#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Quartz
import LaunchServices
import Quartz.CoreGraphics as CG
import datetime
from Cocoa import NSURL
from PIL import Image
import os
import cv2
import numpy as np
import pyautogui
import time


def screenshot(region=None, dpi=72, cv2_format=False):
    if region is None:
        region = CG.CGRectInfinite
    else:
        region = CG.CGRectMake(*region)

    image = CG.CGWindowListCreateImage(
        region,
        CG.kCGWindowListOptionOnScreenOnly,
        CG.kCGNullWindowID,
        CG.kCGWindowImageDefault
    )

    file_name = '.screenshot-{0}.png'.format(datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))
    file_type = LaunchServices.kUTTypePNG
    file_url = NSURL.fileURLWithPath_(file_name)

    dest = Quartz.CGImageDestinationCreateWithURL(file_url, file_type, 1, None)

    properties = {
        Quartz.kCGImagePropertyDPIWidth: dpi,
        Quartz.kCGImagePropertyDPIHeight: dpi,
    }

    Quartz.CGImageDestinationAddImage(dest, image, properties)
    Quartz.CGImageDestinationFinalize(dest)

    if cv2_format:
        image = cv2.imread(file_name)
    else:
        image = Image.open(file_name)

    os.unlink(file_name)
    return image


def locate_all(image_path, confidence=0.9, limit=100, region=None, **kwargs):
    target_image = cv2.imread(image_path)
    source_image  = screenshot(cv2_format=True, region=region)

    target_height, target_width = target_image.shape[:2]

    result = cv2.matchTemplate(target_image, source_image, cv2.TM_CCOEFF_NORMED)
    indexes = np.where(result >= confidence)

    pre_x, pre_y = None, None
    count = 0
    for y, x in zip(*indexes):
        if (
            pre_x is not None and
            pre_y is not None and
            abs(pre_x - x) < target_width / 2.0 and
            abs(pre_y - y) < target_height / 2.0
        ):
            continue

        if region:
            x = x + region[0] * screen_scale
            y = y + region[1] * screen_scale

        founded_region = (x / screen_scale, y / screen_scale, target_width / screen_scale, target_height / screen_scale)
        _update_region_for_cache(image_path, founded_region)
        yield _center(founded_region)

        pre_x = x
        pre_y = y
        count += 1

        if count >= limit:
            break


def locate(image_path, confidence=0.9, retry_times=1, **kwargs):
    locations = tuple()

    # first try to find target in the cached region, where have founded target before
    region = _region_from_cache(image_path)
    if region:
        locations = tuple(locate_all(image_path, confidence=confidence, limit=1, region=region, **kwargs))

    # try to find target in the whole screen if didn't find it in the region
    if len(locations) == 0:
        locations = tuple(locate_all(image_path, confidence=confidence, limit=1, **kwargs))

    if len(locations) > 0:
        return locations[0]

    if retry_times > 0:
        return locate(image_path, confidence=confidence, retry_times=retry_times-1, **kwargs)

    return None


def _center(region):
    return region[0] + region[2] / 2.0, region[1] + region[3] / 2.0


_region_cache = {}


def _region_from_cache(image_path):
    try:
        return _region_cache[image_path]
    except KeyError:
        return None


def _update_region_for_cache(image_path, region):
    ori_region = _region_from_cache(image_path)

    if ori_region:
        x_min = min(ori_region[0], region[0])
        y_min = min(ori_region[1], region[1])
        x_max = max(ori_region[0] + ori_region[2], region[0] + region[2])
        y_max = max(ori_region[1] + ori_region[3], region[1] + region[3])

        region = (x_min, y_min, x_max - x_min, y_max - y_min)

    _region_cache[image_path] = region


def _screen_scale():
    screen_width = Quartz.CGDisplayPixelsWide(Quartz.CGMainDisplayID())
    screen_shot_width, _ = screenshot().size

    return screen_shot_width / screen_width


screen_scale = _screen_scale()


def click(x, y):
    pyautogui.click(x, y)


def double_click(x, y):
    pyautogui.doubleClick(x, y, interval=0.3)


def hold(x, y, last_for=3.0):
    pyautogui.mouseDown(x, y)
    time.sleep(last_for)
    pyautogui.mouseUp()


def drag(from_point, to_point):
    pyautogui.moveTo(*from_point)
    pyautogui.dragTo(*to_point, duration=0.3)
    time.sleep(0.2)


def drag_through(points):
    count = len(points)

    if count < 2:
        return

    from_point = points[0]
    to_points = points[1:]

    pyautogui.mouseDown(*from_point)

    for point in to_points:
        pyautogui.moveTo(point, duration=0.2)

    pyautogui.mouseUp()
    time.sleep(0.2)


def press(key):
    pyautogui.press(key)


def locate_and_click(image_path, **kwargs):
    location = locate(image_path, **kwargs)
    if not location:
        return False

    click(*location)
    return True
