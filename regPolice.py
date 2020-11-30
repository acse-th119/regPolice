#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 11/18/20 9:33 PM
# @Author  : Mongo
# @Email   : caesarhtx@163.com
# @File    : regPolice.py
# @Software: PyCharm

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging
import os.path
import time
import datetime
import re
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)

rq = time.strftime('%Y%m%d_%H%M', time.localtime(time.time()))
log_path = os.getcwd()
log_name = os.path.join(log_path, rq + '.log')
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)

logger.addHandler(fh)
timeS = 16
timeE = 23


def selenium_driver(url_login):
    '''creater a driver using selenium which may not be forbidden'''
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument("--proxy-server=http://60.177.229.177：18118")

    # path to the selenium chrome driver
    driver = webdriver.Chrome(r'C:\Users\mongo\Documents\pythonProjects\regPolice\chromedriver_win32\chromedriver.exe',
                              options=chrome_options)
    #time.sleep(10)# 10秒
    while True:
        try:
            driver.get(url_login)
            break
        except:
            pass

    return driver


def send_email(title, content):
    # load config
    with open('mail_keyword.json') as fp:
        mail_keyword = json.load(fp)
    
    mail_host = mail_keyword['mail_host']
    mail_user = mail_keyword['mail_user']
    mail_pass = mail_keyword['mail_pass']
    sender = mail_keyword['sender']
    receivers = mail_keyword['receivers']

    message = MIMEMultipart('related')
    content = MIMEText(str(content), 'plain', 'utf-8')
    message.attach(content)
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  
        smtpObj.login(mail_user, mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        logger.warning('Mail has been send successfully.')
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)


def in_weekday(time_str):
    # send email on specific weekday
    text = time_str
    text_list = text.split()
    text_list[0] = re.match('\d+', text_list[0]).group()
    text = ' '.join(text_list)
    outweekday = datetime.datetime.strptime(text, '%d %B %Y').weekday()
    return outweekday in [0,1,2,3,4,5,6], outweekday # [2,3,4], outweekday


if __name__ == '__main__':
    # home page of police office web
    police_browser = selenium_driver('https://www.ovroregistrations.org/new-appointment#student-select')
    
    while True:
        try:
            if police_browser.find_element_by_xpath("//*[contains(text(),'Your postcode')]"):
                police_browser.find_element_by_xpath('//*[@id="inputPostcode"]').send_keys('SW7 2LT')
                time.sleep(1)
                police_browser.find_element_by_xpath('//*[@id="check-postcode"]').click()
                time.sleep(1)
                police_browser.find_element_by_xpath('//*[@id="student-radio-yes"]').click()
                time.sleep(1)
                police_browser.find_element_by_xpath('//*[@id="student-selector"]').click()
                time.sleep(15)
        except:
            pass
        hour_now = int(time.strftime("%H"))
        time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            date_element = police_browser.find_element_by_xpath("//*[text()[contains(.,'Jan') or contains(.,'Dec') or contains(.,'Nov')]]")  # January December November
            if date_element:
                logger.warning('Found it, Registration time in weekday {}: {}'.format(int(in_weekday(date_element.text)[1])+1,date_element.text))
                # if (hour_now <= timeS or hour_now >= timeE) and in_weekday(date_element.text)[0]:
                send_email('Police Registration Booking Alarm', "Registration Time: {}\n\n\n\nCheck on {}\n".format(date_element.text, time_now))
                police_browser.refresh()
                time.sleep(15)
        except Exception as e:
            logger.info('{}: noting fetched, crash caused by {}'.format(time_now, str(e)[:24]))
            try:
                police_browser.refresh()
            except:
                continue

        time.sleep(15)
