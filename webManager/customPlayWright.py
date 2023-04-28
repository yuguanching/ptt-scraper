import configSetting
from playwright.sync_api import sync_playwright


class browserManager():
    def __init__(self) -> None:
        self.browser = sync_playwright().start().chromium.launch(headless=False)

    def closeBrowser(self):
        self.browser.close()

# 公共的模擬瀏覽器實體
browser_manager = browserManager()