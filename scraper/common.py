import gevent
import grequests
import requests
import re as regularExpression
from bs4 import BeautifulSoup
from playwright.sync_api import Browser
from abc import ABC, abstractmethod


class paginationChecker(ABC):
    @abstractmethod
    def checkPages(targetType: str, targetPage: str, browser: Browser) -> list:
        pass


def grequestFetchHTML(sourceList: list) -> list:
    request_pool = (grequests.get(link) for link in sourceList)
    responses = grequests.map(request_pool)

    return responses
