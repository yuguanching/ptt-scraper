import configSetting
if configSetting.os_type == "mac":
    from gevent import monkey
    monkey.patch_all()
from tool import Auxiliary,thread
from ioService import parser
from scraper import categoryPosts, common
from pprint import pprint
from playwright.async_api import async_playwright
import asyncio
import nest_asyncio
nest_asyncio.apply()

target_urls = configSetting.json_array_data["targetURL"]
target_names = configSetting.json_array_data["targetName"]
category_posts_scraper = categoryPosts.categoryPosts()

async def getAllPostsLink(postsAllPages:list)->list:
    posts_link_list = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=configSetting.playwirght_headless)
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [asyncio.ensure_future(category_posts_scraper.parsePostsLink(page, browser)) for page in postsAllPages]
        loop.run_until_complete(asyncio.gather(*tasks))
        await browser.close()
    for task in tasks:
        posts_link_list.extend(task.result())

    return posts_link_list    

for target_url, target_name in zip(target_urls, target_names):

    Auxiliary.checkDirAndCreate(target_name)
    posts_all_pages = []
    posts_link_list = []

    posts_all_pages = category_posts_scraper.checkPages("分類文章", target_url)
    # posts_all_pages = [
    #     "https://www.pttweb.cc/bbs/Gossiping/page?n=4130025",
    #     "https://www.pttweb.cc/bbs/Gossiping/page?n=4130000"
    #     ]

    posts_all_pages_group = Auxiliary.listPartition(posts_all_pages, configSetting.asyncio_patch_number)

    for group in posts_all_pages_group:
        temp_result = asyncio.run(getAllPostsLink(group))
        posts_link_list.extend(temp_result)
    
    pprint(posts_link_list)
    print(len(posts_link_list))
