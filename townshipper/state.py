#!/usr/bin/env python
# -*- coding: utf-8 -*-

import window


class Action():
    def __init__(self, description, handler, next_state=None, help=None):
        self._description = description
        self._handler = handler
        self._next_state = next_state
        self._help = help



    def __repr__(self):
        if self._help:
            return '操作：{name}({help})'.format(name=self._description, help=self._help)

        return '操作：' + self._description

    def __call__(self, *args, **kwargs):
        global  current_state
        if self._handler(*args, **kwargs):
            current_state = self._next_state

_main_state = []
_barn_state = []
_upgrade_state = []
_item_detail_state = []

_main_state += [
    Action('打开仓库', window.Barn.open, _barn_state),
]

_barn_state += [
    Action('商品详情', window.Barn.detail_for_item, _item_detail_state, '参数说明：必须传入一个商品名称'),
    Action('升级', window.Barn.upgrade, _upgrade_state),
    Action('返回', window.back, _main_state)
]

_upgrade_state += [
    Action('返回', window.back, _barn_state)
]

_item_detail_state += [
    Action('出售', window.Barn.sell),
    Action('数量 +1', window.Barn.increase_sell_amount),
    Action('数量 -1', window.Barn.decrease_sell_amount),
    Action('返回', window.back, _barn_state),
]

current_state = _main_state

