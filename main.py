# from gevent import monkey
# # monkey.patch_all()
import grequests
from tool import Auxiliary
from ioService import parser
from scraper import auther, common
from pprint import pprint
from playwright.sync_api import sync_playwright
import configSetting


target_urls = configSetting.json_array_data["targetURL"]
target_names = configSetting.json_array_data["targetName"]
auther_data_scraper = auther.auther()
autherBuilder = parser.autherDataBuilder()

for target_url, target_name in zip(target_urls, target_names):

    Auxiliary.checkDirAndCreate(target_name)

    comments_data_list = []
    comments_all_pages = []
    nickname_data_list = []
    nickname_all_pages = []
    posts_data_list = []
    posts_all_pages = []
    posts_link_list = []

    overview_data = dict()

    with sync_playwright() as p:
        for browser_type in [p.chromium]:
            browser = browser_type.launch(headless=configSetting.playwirght_headless)

            overview_data = auther_data_scraper.parseOverviewData(targetPage=target_url, browser=browser)
            comments_all_pages = auther_data_scraper.checkPages("留言", targetPage=overview_data["comments"]["subpage_link"], browser=browser)
            nickname_all_pages = auther_data_scraper.checkPages("暱稱", targetPage=overview_data["nickname"]["subpage_link"], browser=browser)
            posts_all_pages = auther_data_scraper.checkPages("發文", targetPage=overview_data["posts"]["subpage_link"], browser=browser)
            browser.close()

    # 發文
    posts_pages_responses = common.grequestFetchHTML(posts_all_pages)
    for resp in posts_pages_responses:
        posts_link_list.extend(auther_data_scraper.parsePostsLink(resp.text))

    posts_data_responses = common.grequestFetchHTML(posts_link_list)
    for resp, url in zip(posts_data_responses, posts_link_list):
        posts_data_page_result = auther_data_scraper.parsePostsData(resp.text, overview_data["auther"]["name"], targetURL=url)
        posts_data_list.extend(posts_data_page_result)

    autherBuilder.postsBuilder.buildDataSet(posts_data_list, target_name, 'w')

    # 留言
    comments_responses = common.grequestFetchHTML(comments_all_pages)
    for resp in comments_responses:
        comments_data_page_result = auther_data_scraper.parseCommentsData(resp.text, overview_data["auther"]["name"])
        comments_data_list.extend(comments_data_page_result)

    autherBuilder.commentsBuilder.buildDataSet(comments_data_list, target_name, 'a')

    # 暱稱
    nickname_responses = common.grequestFetchHTML(nickname_all_pages)
    for resp in nickname_responses:
        nickname_data_page_result = auther_data_scraper.parseNicknameData(resp.text, overview_data["auther"]["name"])
        nickname_data_list.extend(nickname_data_page_result)

    autherBuilder.nicknameBuilder.buildDataSet(nickname_data_list, target_name, 'a')
