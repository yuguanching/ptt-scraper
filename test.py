import grequests
import requests
import re
import ipinfo
import configSetting
import time

from tool import Auxiliary
from scraper import auther
from pprint import pprint
from ioService import parser
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

fn = 4115925
aa = 4129800

for i in range(aa, fn-1, -25):
    print(i)
# url = "https://www.pttweb.cc/bbs/Gossiping/page?n=4129150"


# with sync_playwright() as p:
#     for browser_type in [p.chromium]:
#         browser = browser_type.launch(headless=configSetting.playwirght_headless)
#         page = browser.new_page()
#         page.goto(url)
#         time.sleep(2)
#         post_title_elements = page.query_selector("div.mt-2").query_selector_all("div.e7-container")

#         flag = True
#         for pte in post_title_elements:
#             pte.hover()
#             time.sleep(0.1)
#             meta_data = pte.query_selector("div.e7-meta-container").query_selector("div.e7-grey-text").text_content()
#             date = str(re.findall(r"[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+:[0-9]+", meta_data)[0]).replace("/", "-")+":00"
#             if Auxiliary.dateCompare(date):
#                 continue
#             else:
#                 flag = False
#                 break
# parser.buildCollectData(lll,"asdf2004")

# ip_address = "209.58.188.40"

# handler = ipinfo.getHandler(configSetting.ipinfo_access_token)
# details = handler.getDetails(ip_address=ip_address)
# print(details.all)
