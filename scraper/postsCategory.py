import re as regularExpression
import configSetting
import traceback
import time
import requests
from tool import Auxiliary
from bs4 import BeautifulSoup
from pprint import pprint
from playwright.sync_api import Browser
from scraper import common


class postsCategory(common.paginationChecker):
    def checkPages(self, targetType: str, targetPage: str, browser: Browser) -> list:
        page_link_list = []
        max_page_number = 0
        page_path = ""
        page = browser.new_page()
        page.goto(targetPage)

        next_page_url = page.query_selector(
            "div.e7-no-outline-all-descendants.e7-btn-no-focus.my-4.e7-page-navigation").query_selector(
            "a:not(.v-btn--disabled).blue.darken-3.v-btn.v-btn--router.v-btn--small.theme--dark").get_attribute("href")
        page_path, max_page_number = regularExpression.search(r"(.*?)=([0-9]+)", str(next_page_url)).groups()
        max_page_number = int(max_page_number) + 25
        page_path = configSetting.pttRootURL + page_path + "="
        page.close()
        # print(page_number//2)

        # 二分搜尋法,找到用戶設定時間的貼文分頁所在處
        left, right = 0, max_page_number
        final_number = 0
        while True:
            mid = left + (right-left)//2
            page = browser.new_page()
            page.goto(page_path + str(mid))
            time.sleep(2)
            post_title_elements = page.query_selector("div.mt-2").query_selector_all("div.e7-container")

            flag_list = []
            inner_flag = True
            for pte in post_title_elements:
                pte.hover()
                time.sleep(0.1)
                meta_data = pte.query_selector("div.e7-meta-container").query_selector("div.e7-grey-text").text_content()
                date = str(regularExpression.findall(r"[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+:[0-9]+", meta_data)[0]).replace("/", "-")+":00"
                if Auxiliary.dateCompare(date):
                    flag_list.append(True)
                    inner_flag = True
                else:
                    flag_list.append(False)
                    inner_flag = False
            if (True in flag_list) and (False in flag_list):
                final_number = mid
                page.close()
                break
            else:
                if inner_flag:
                    right = mid
                else:
                    left = mid
            page.close()
        # 符合ptt-web 25一個分頁的規則
        if final_number % 25 != 0:
            final_number = (final_number//25) * 25 + 25
        for i in range(max_page_number, final_number-1, -25):
            page_link_list.append(page_path+str(i))
        return page_link_list
