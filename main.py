import grequests
import configSetting

from gevent import monkey, select
monkey.patch_all()
from auther import overview, nickname, common, comments, posts
from ioService import parser
from playwright.sync_api import sync_playwright
from pprint import pprint

target_page = "https://www.pttweb.cc/user/asdf2004"
comments_data_list = []
comments_all_pages = []
nickname_data_list = []
nickname_all_pages = []
posts_data_list = []
posts_all_pages = []
posts_link_list = []

overview_data = dict()

with sync_playwright() as p :
    for browser_type in [p.chromium]:
        browser  = browser_type.launch(headless=configSetting.playwirght_headless)

        overview_data = overview.parseOverviewData(targetPage=target_page, browser=browser)
        comments_all_pages = common.checkAllPaginations("留言",targetPage=overview_data["comments"]["subpage_link"], browser=browser)
        nickname_all_pages = common.checkAllPaginations("暱稱",targetPage=overview_data["nickname"]["subpage_link"], browser=browser)
        posts_all_pages = common.checkAllPaginations("發文",targetPage=overview_data["posts"]["subpage_link"], browser=browser)
        browser.close()

# 發文
posts_pages_responses = common.grequestFetchHTML(posts_all_pages)
for resp in posts_pages_responses:
    posts_link_list.extend(posts.parsePostsLink(resp.text))


posts_data_responses = common.grequestFetchHTML(posts_link_list)
for resp, url in zip(posts_data_responses, posts_link_list):
    posts_data_page_result = posts.parsePostsData(resp.text, overview_data["auther"]["name"],targetURL=url)
    posts_data_list.extend(posts_data_page_result)

parser.buildCollectData(posts_data_list, overview_data["auther"]["name"])
# # 留言
# comments_responses = common.grequestFetchHTML(comments_all_pages)
# for resp in comments_responses:
#     comments_data_page_result = comments.parseCommentsData(resp.text, overview_data["auther"]["name"])
#     comments_data_list.append(comments_data_page_result)
    

# # 暱稱
# nickname_responses = common.grequestFetchHTML(nickname_all_pages)
# for resp in nickname_responses:
#     nickname_data_page_result = nickname.parseNicknameData(resp.text, overview_data["auther"]["name"])
#     nickname_data_list.append(nickname_data_page_result)