#!/usr/bin/env python
# -*- coding: utf-8 -*-

import messenger
import game
import window


AVAILABLE_COMMANDS = "open"


def check_and_handle_new_command():
    mail = messenger.receive_new_mail()

    if not mail:
        return

    _, subject = mail
    args = subject.split()
    command = args[0].lower()

    if command not in AVAILABLE_COMMANDS.split(','):
        _failure_reply(subject, "Can't Find This Command!")
        return

    handler = globals()[command]
    flag, message = handler(args[1:])


def _failure_reply(subject, message):
    subject = '[FAILED] ' + subject
    messenger.send_mail(subject, message, window.screenshot())


def _success_reply(subject, message):
    subject = '[SUCCEED] ' + subject
    messenger.send_mail(subject, message, window.screenshot())


def _open(window_name):
    pass
