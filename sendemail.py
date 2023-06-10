# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 4/9/2023 14:07
# @Author : Xiaosheng Jin
# @Email : xiaosheng7@126.com
# @File : email.py
# @Software: PyCharm

import argparse
import os
import smtplib
import sys
import time
import zipfile
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def zip_folder(folder_path, output_path):
    """
    压缩文件夹
    :param folder_path: 要压缩的文件夹的路径
    :param output_path: 压缩文件的输出路径
    zip_folder('/path/to/folder', '/path/to/output.zip')
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as f:
        # 递归遍历文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # 获取文件的绝对路径
                file_path = os.path.join(root, file)
                # 将文件添加到压缩文件中
                f.write(file_path, os.path.relpath(file_path, folder_path))


def zip_file(file_path, output_path):
    """
    压缩文件
    :param file_path: 要压缩的文件的路径
    :param output_path: 压缩文件的输出路径
    zip_file('/path/to/file', '/path/to/output.zip')
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as f:
        # 将文件添加到压缩文件中
        f.write(file_path, os.path.basename(os.path.basename(file_path)))


def cmd_line():
    default_account = {
        'user': '16*******2@qq.com',
        'pwd': 'wtczpp*******bdcfsda'
    }

    parser = argparse.ArgumentParser(description='=====>>> 参数释义 <<<=====')
    parser.add_argument('-u',
                        '--user',
                        type=str,
                        default=default_account['user'],
                        help='发件人邮箱')
    parser.add_argument('-p',
                        '--pwd',
                        type=str,
                        default=default_account['pwd'],
                        help='邮箱授权码(不是密码！！！)')
    parser.add_argument('-r',
                        '--receiver',
                        type=str,
                        required=True,
                        help='收件人邮箱')
    parser.add_argument('-c',
                        '--cc',
                        type=str,
                        help='抄送邮箱')
    parser.add_argument('-b',
                        '--bcc',
                        type=str,
                        help='秘抄邮箱')
    parser.add_argument('-t',
                        '--title',
                        type=str,
                        help='邮件标题')
    parser.add_argument('-w',
                        '--word',
                        type=str,
                        help='邮件正文文本内容或路径')
    parser.add_argument('-f',
                        '--file',
                        type=str,
                        help='邮件附件路径')

    args = parser.parse_args()
    user = args.user
    pwd = args.pwd
    receiver = args.receiver
    if args.cc:
        cc_list = args.cc
    else:
        cc_list = ''
    if args.bcc:
        bcc_list = args.bcc
    else:
        bcc_list = ''

    title = args.title

    if args.word:
        if os.path.isfile(args.word):
            with open(args.word, mode='r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.word
    else:
        text = ''
    if args.file:
        attachment = args.file
    else:
        attachment = ''
    return user, pwd, receiver, cc_list, bcc_list, title, text, attachment


class Email:
    def __init__(self, user, pwd, receiver, cc_list, bcc_list, title, text, attachment):
        smtpserver = {'gmail.com': 'smtp.gmail.com', 'yahoo.com': 'smtp.mail.yahoo.com',
                      'outlook.com': 'smtp.live.com',
                      'hotmail.com': 'smtp.live.com', 'aol.com': 'smtp.aol.com', 'gmx.com': 'mail.gmx.com',
                      'zoho.com': 'smtp.zoho.com', 'icloud.com': 'smtp.mail.me.com', 'mail.com': 'smtp.mail.com',
                      'protonmail.com': 'smtp.protonmail.com', 'qq.com': 'smtp.qq.com', '163.com': 'smtp.163.com',
                      '126.com': 'smtp.126.com'}
        self.user = user
        self.pwd = pwd
        if self.user.split('@')[-1] in smtpserver:
            self.host = smtpserver[self.user.split('@')[-1]]
            self.port = 465
        else:
            host = input('请输入smtp服务器地址(q退出):')
            if host == 'q':
                sys.exit()
            else:
                self.host = host
            port = int(input('请输入smtp服务器地址(q退出):'))
            if port == 'q':
                sys.exit()
            else:
                self.port = port
        self.receiver = receiver
        self.cc = cc_list
        self.bcc = bcc_list
        self.title = title
        self.text = text
        self.attachment = attachment
        print(self.user, self.pwd, self.host, self.port, self.receiver, self.cc, self.bcc, self.title, self.text,
              self.attachment)

    def set_msg(self):
        # 创建邮件实体
        msg = MIMEMultipart('mixed')  # mixed,可以发纯文本和附件

        # 邮件标题
        msg['Subject'] = Header(self.title, 'utf-8').encode()

        # 收、发件人 信息
        msg['From'] = self.user
        msg['To'] = self.receiver
        msg['Cc'] = self.cc
        msg['Bcc'] = self.bcc

        # 邮件正文
        # MIMEText()第一个参数也可以是任意字符串，第二个参数是纯文本格式，第三个参数是编码方式
        text_plain = MIMEText(self.text, 'plain', 'utf-8')
        msg.attach(text_plain)  # 将正文内容添加到msg中

        # 添加邮件附件
        if self.attachment:
            paths = self.attachment.split()
            for path in paths:
                tmp = os.path.basename(path).split('.')[0]
                zip_name = os.path.join(os.path.dirname(os.path.abspath(path)), f'{tmp}.zip')
                if os.path.isdir(path):
                    try:
                        zip_folder(path, zip_name)
                    except Exception as e:
                        print(f'压缩文件夹{path}失败,报错信息如下：')
                        print(e)
                else:
                    try:
                        zip_file(path, zip_name)
                    except Exception as e:
                        print(f'压缩文件{path}失败,报错信息如下：')
                        print(e)

                with open(zip_name, mode='rb') as b:
                    file_name = f'{tmp}.zip'
                    attach_file = MIMEApplication(b.read())
                    attach_file.add_header('Content-Disposition', 'attachment', filename=file_name)
                    msg.attach(attach_file)  # 将附件插入邮件

                os.remove(zip_name)

        # 将邮件作为一个字符串返回，方便在smtp中传递
        return msg.as_string()

    def send_email(self):
        smtp = smtplib.SMTP_SSL(self.host, self.port)
        try:
            smtp.login(self.user, self.pwd)
            print('成功登录邮箱')
        except Exception as e:
            print('无法连接smtp服务器登录邮箱，请检查网络或账号密码！')
            print(e)
        msg = self.set_msg()
        try:
            smtp.sendmail(self.user, self.receiver.split(',') + self.cc.split(',') + self.bcc.split(','), msg)
            time.sleep(3)  # 考虑到网速预留三秒发送时间，也可以不要
            smtp.quit()
            print('邮件发送成功！')
        except Exception as e:
            print('邮件发送失败！报错信息如下：')
            print(e)


if __name__ == '__main__':
    user, pwd, receiver, cc_list, bcc_list, title, text, attachment = cmd_line()
    email = Email(user, pwd, receiver, cc_list, bcc_list, title, text, attachment)
    email.send_email()

