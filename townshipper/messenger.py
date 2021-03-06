#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import smtplib
from email.utils import formataddr
from email.header import Header
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email import encoders
import email
import imaplib
import socket

# --------------------------------------------
# Setup Config

CONFIG_FILE_PATH = 'messenger.ini'

_from_email = None
_from_password = None
_from_smtp_server = None
_from_smtp_port = None
_from_imap_server = None
_from_imap_port = None

_to_email = None


def init():
    config = _config()

    if not config.has_section('from'):
        if not _setup_from_config(config):
            return False

    if not config.has_section('to'):
        if not _setup_to_config(config):
            return False

    global _from_email, _from_password, _from_smtp_server, _from_smtp_port, _from_imap_server, _from_imap_port, _to_email

    _from_email = config.get('from', 'email')
    _from_password = config.get('from', 'password')
    _from_smtp_server = config.get('from', 'smtp_server')
    _from_smtp_port = config.get('from', 'smtp_port')
    _from_imap_server = config.get('from', 'imap_server')
    _from_imap_port = config.get('from', 'imap_port')
    _to_email = config.get('to', 'email')

    print('所有设置已完成，你可以打开 {0} 文件编辑已有的设置！\n'.format(CONFIG_FILE_PATH))

    return True


def _config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)

    return config


def _setup_from_config(config):
    from_email = input('请输入用于发送游戏信息的邮箱账号：\n')
    from_password = input('请输入密码：')
    from_smtp_server = input('请输入邮箱发送服务器(SMTP)：\n')
    from_smtp_port = input('请输入端口号(TLS)：\n')
    from_imap_server = input('请输入邮箱接收服务器(IMAP):\n')
    from_imap_port = input('请输入端口号：\n')

    print('开始向邮箱服务器验证信息，请稍候...\n')

    try:
        server = smtplib.SMTP(from_smtp_server, from_smtp_port)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(from_email, from_password)
        server.quit()

        config.add_section('from')
        config.set('from', 'email', from_email)
        config.set('from', 'password', from_password)
        config.set('from', 'smtp_server', from_smtp_server)
        config.set('from', 'smtp_port', from_smtp_port)
        config.set('from', 'imap_server', from_imap_server)
        config.set('from', 'imap_port', from_imap_port)
        with open(CONFIG_FILE_PATH, 'w') as file:
            config.write(file)

        print('已完成发送邮箱相关设置\n')

        return True
    except smtplib.SMTPAuthenticationError:
        print('账号密码不正确')
    except smtplib.SMTPHeloError:
        print('服务配置不正确')
    except TimeoutError:
        print('连接失败，请重新配置！')

    return False


def _setup_to_config(config):
    to_email = input('请输入用于接收游戏信息及发送操作命令的邮箱：\n')

    config.add_section('to')
    config.set('to', 'email', to_email)

    with open(CONFIG_FILE_PATH, 'w') as file:
        config.write(file)

    print('已完成接收邮箱相关设置\n')

    return True

# --------------------------------------------
# Mail


def _smtp_server(timeout_retry_time=10, timeout=300):
    print('开始连接邮箱SMTP服务器...')
    try:

        server = smtplib.SMTP(_from_smtp_server, _from_smtp_port, timeout=timeout)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(_from_email, _from_password)

        print('已成功连接SMTP服务器')

        return server
    except TimeoutError:
        if timeout_retry_time:
            return _smtp_server(timeout_retry_time=timeout_retry_time-1)
        else:
            print('连接邮箱SMTP服务器超时！')
            return None
    except Exception as e:
        print('连接邮箱SMTP服务器失败：', e)
        return None


def send_mail(subject, content, image=None):
    server = _smtp_server()

    if not server:
        return False

    msg = MIMEMultipart()
    msg['From'] = formataddr((Header('Auto Shipper', 'utf8').encode(), _from_email))
    msg['Subject'] = Header(subject, 'utf8').encode()

    if image:
        image.thumbnail((1000, 1000))
        image.save('tmp/thumbnail.png')
        with open('tmp/thumbnail.png', 'rb') as file:
            msg_image = MIMEBase('image', 'png', filename='attachment.png')
            msg_image.add_header('Content-Disposition', 'attachment', filename='attachment.png')
            msg_image.add_header('Content-ID', '<0>')
            msg_image.add_header('X-Attachment-Id', '0')

            msg_image.set_payload(file.read())

            encoders.encode_base64(msg_image)

            msg.attach(msg_image)

            content += '<p><img src="cid:0"></p>'

    msg.attach(MIMEText(content, 'html', 'utf8'))

    server.sendmail(_from_email, _to_email, msg.as_string())
    server.quit()
    return True


def _imap_server(timeout_retry_time=10, timeout=300):
    print('开始连接邮箱IMAP服务器...')
    try:
        socket.setdefaulttimeout(timeout)
        server = imaplib.IMAP4_SSL(_from_imap_server, _from_imap_port)
        server.login(_from_email, _from_password)

        print('已成功连接到IMAP服务器')

        return server
    except TimeoutError:
        if timeout_retry_time:
            return _imap_server(timeout_retry_time=timeout_retry_time - 1)
        else:
            print('连接邮箱IMAP服务器超时！')
            return None
    except Exception as e:
        print('连接邮箱IMAP服务器失败：', e)
        return None


def receive_new_mail():
    server = _imap_server()
    if not server:
        return None

    print('开始检测新邮件...')
    server.select()
    search_result = server.uid('search', None, 'UnSeen From "{0}"'.format(_to_email))
    mail_uids = (search_result[1][0].decode('utf8')).split()

    if not mail_uids:
        print('没有任何新邮件')
        return None

    uid = mail_uids[0]

    ret_code, fetch_result = server.uid('fetch', uid, '(RFC822)')
    if ret_code != 'OK':
        print('获取邮件失败:', uid, ret_code)
        return None

    msg = email.message_from_bytes(fetch_result[0][1])
    subject = msg['subject']

    print('获取到新邮件：', subject)

    return uid, subject
