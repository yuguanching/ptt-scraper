import gevent
import grequests
import requests
import re as regularExpression
from bs4 import BeautifulSoup
from playwright.sync_api import Browser




def checkAllPaginations(type:str, targetPage:str, browser:Browser)->list:

    print(f"檢查{type}的總頁數")

    page_pattern = r"(.*?)\=([0-9]+)"
    pages_list = []
    pages_list.append(targetPage)
    tail_page_url = ""
    page_number = 0
    
    page = browser.new_page()
    page.goto(targetPage)

    tail_point_element = page.query_selector("a[data-v-c841833e]:has-text('尾頁')")

    if tail_point_element is not None:
        tail_page_url = str(tail_point_element.get_attribute("href"))
        res = regularExpression.search(page_pattern, tail_page_url)
        page_number = int(res.group(2))
        for i in range(1,page_number+1):
            pages_list.append(targetPage + f"&page={i}" )

    print(f"檢查完成, {type}共有{page_number+1}個分頁")
    page.close()
    return pages_list


def grequestFetchHTML(sourceList:list)->list:
    request_pool = (grequests.get(link) for link in sourceList)
    responses = grequests.map(request_pool)

    return responses