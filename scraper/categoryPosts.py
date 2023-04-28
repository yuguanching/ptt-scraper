import re as regularExpression
import configSetting
import traceback
import time
import requests

from webManager import customPlayWright
from playwright.async_api import async_playwright, Browser, Route, Request
from tool import Auxiliary
from bs4 import BeautifulSoup
from pprint import pprint
from playwright.sync_api import Browser
from scraper import common



class categoryPosts(common.paginationChecker, common.postsScraper):
    def checkPages(self, targetType: str, targetPage: str) -> list:

        print(f"檢查{targetType}的總頁數")

        page_link_list = []
        max_page_number = 0
        page_path = ""

        page = customPlayWright.browser_manager.browser.new_page()
        # 不加載圖片類型的資源
        page.route("**/*", lambda route: route.abort()
        if route.request.resource_type =="image"
        else route.continue_()
        )
        page.goto(targetPage)

        next_page_loc = page.query_selector(
            "div.e7-no-outline-all-descendants.e7-btn-no-focus.my-4.e7-page-navigation >> a:not(.v-btn--disabled).blue.darken-3.v-btn.v-btn--router.v-btn--small.theme--dark")
        next_page_url = next_page_loc.get_attribute("href")
        page_path, max_page_number = regularExpression.search(r"(.*?)=([0-9]+)", str(next_page_url)).groups()
        max_page_number = int(max_page_number) + 25
        page_path = configSetting.pttRootURL + page_path + "="
        page.close()

        # 二分搜尋法,找到用戶設定時間的貼文分頁所在處
        left, right = 0, max_page_number
        final_page_number = 0
        while True:
            mid = left + (right-left)//2
            page = customPlayWright.browser_manager.browser.new_page()
            page.goto(page_path + str(mid))
            time.sleep(2)
            post_block_elements = page.query_selector_all("div.mt-2 >> div.e7-container")

            flag_list = []
            inner_flag = True
            for pbe in post_block_elements:
                pbe.hover()
                time.sleep(0.1)
                meta_data_loc = pbe.query_selector("div.e7-meta-container >> div.e7-grey-text")
                meta_data = meta_data_loc.text_content()
                date = str(regularExpression.findall(r"[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+:[0-9]+", meta_data)[0]).replace("/", "-")+":00"
                if Auxiliary.dateCompare(date):
                    flag_list.append(True)
                    inner_flag = True
                else:
                    flag_list.append(False)
                    inner_flag = False
            if (True in flag_list) and (False in flag_list):
                final_page_number = mid
                page.close()
                break
            else:
                if inner_flag:
                    right = mid
                else:
                    left = mid
            page.close()
        # 符合ptt-web 25一個分頁的規則
        if final_page_number % 25 != 0:
            final_page_number = (final_page_number//25) * 25 + 25
        for i in range(max_page_number, final_page_number-1, -25):
            page_link_list.append(page_path+str(i))

        print(f"檢查完成, {targetType}共有{len(page_link_list)}個分頁")

        return page_link_list

    
    async def parsePostsLink(self, targetPage: str, browser:Browser) -> list:

        print(f"{targetPage} 分頁處理中")
        post_link_list = []
        
        context = await browser.new_context()
        page = await context.new_page()

        # 不加載圖片類型的資源(異步寫法, 不加載的類型可擴充)
        async def blockResource(route:Route, request:Request):
            if request.resource_type in {'image'}:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", blockResource)
        await page.goto(targetPage)
        post_block_elements = await page.query_selector_all("div.mt-2 >> div.e7-container")
        for pbe in post_block_elements:
            await pbe.hover()
            href_loc = await pbe.query_selector("div.e7-right.ml-2 >> div.e7-right-top-container.e7-no-outline-all-descendants >> a")
            post_link = configSetting.pttRootURL + await href_loc.get_attribute("href")
            meta_data_loc = await pbe.query_selector("div.e7-meta-container >> div.e7-grey-text")
            meta_data = await meta_data_loc.text_content()
            date = str(regularExpression.findall(r"[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+:[0-9]+", meta_data)[0]).replace("/", "-")+":00"
            post_title_dict = dict(post_link=post_link, date=date)
            post_link_list.append(post_title_dict)
        
        await page.close()
        await context.close()
        return post_link_list