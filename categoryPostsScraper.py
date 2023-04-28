import grequests
from tool import Auxiliary
from ioService import parser
from scraper import common, postsCategory
from pprint import pprint
from playwright.sync_api import sync_playwright
import configSetting


target_urls = configSetting.json_array_data["targetURL"]
target_names = configSetting.json_array_data["targetName"]
category_posts_scraper = postsCategory.postsCategory()

for target_url, target_name in zip(target_urls, target_names):

    Auxiliary.checkDirAndCreate(target_name)
    posts_link_list = []
    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch(headless=configSetting.playwirght_headless)
            posts_link_list = category_posts_scraper.checkPages("分類文章", target_url, browser)

    print(posts_link_list)
