import configSetting
if configSetting.os_type == "mac":
    from gevent import monkey
    monkey.patch_all()
import requests
import re
import asyncio
import nest_asyncio
import time
nest_asyncio.apply()

# from webManager import customPlayWright
from playwright.sync_api import sync_playwright
from tool import Auxiliary, thread
# from scraper import auther, common, categoryPosts
from pprint import pprint
from ioService import parser
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor




# async def parsePostsLink(targetPage: str, browser:Browser) -> list:

#     print(f"{targetPage} 分頁處理中")
#     post_link_list = []
    
#     context = await browser.new_context()
#     page = await context.new_page()
#     await page.goto(targetPage)
#     post_block_elements = await page.query_selector_all("div.mt-2 >> div.e7-container")
#     for pbe in post_block_elements:
#         await pbe.hover()
#         href_loc = await pbe.query_selector("div.e7-right.ml-2 >> div.e7-right-top-container.e7-no-outline-all-descendants >> a")
#         post_link = configSetting.pttRootURL + await href_loc.get_attribute("href")
#         meta_data_loc = await pbe.query_selector("div.e7-meta-container >> div.e7-grey-text")
#         meta_data = await meta_data_loc.text_content()
#         date = str(re.findall(r"[0-9]+\/[0-9]+\/[0-9]+\s[0-9]+:[0-9]+", meta_data)[0]).replace("/", "-")+":00"
#         post_title_dict = dict(post_link=post_link, date=date)
#         post_link_list.append(post_title_dict)
    
#     await page.close()
#     await context.close()
#     return post_link_list

# async def runTest():
#     async with async_playwright() as p:
#         posts_all_pages = ["https://www.pttweb.cc/bbs/Gossiping/page?n=4130025","https://www.pttweb.cc/bbs/Gossiping/page?n=4130000"]
#         test_all_pages = posts_all_pages[0:2]
#         browser = await p.chromium.launch(headless=configSetting.playwirght_headless)

#         loop = asyncio.get_event_loop()
#         asyncio.set_event_loop(loop)
#         tasks = [asyncio.ensure_future(parsePostsLink(page, browser)) for page in test_all_pages]
#         loop.run_until_complete(asyncio.wait(tasks))
        
#         await browser.close()
    
#     for task in tasks:
#         print(task.result())
    

# asyncio.run(runTest())

with sync_playwright() as p :
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 不加載圖片類型的資源
    page.route("**/*", lambda route: route.abort()
    if route.request.resource_type =="image"
    else route.continue_()
    )
    page.goto("https://www.pttweb.cc/bbs/Gossiping/page?n=4130850")

    time.sleep(100)