import time
import re as regularExpression
import configSetting
from playwright.sync_api import Browser


re_pattern = r"(.*?) ([0-9]+?) \((.*?)%\)"
pcne_pattern = r"(.*?)\: ([0-9]+)"

def parseOverviewData(targetPage :str, browser: Browser) -> dict:
    overview_data = dict(
        posts=dict(
            value = "",
            subpage_link= "",
            thumb=dict(value="",percentage=""),
            arrow=dict(value="",percentage=""),
            boo=dict(value="",percentage="")
            ),
        comments=dict(
            value = "",
            subpage_link= "",
            thumb=dict(value="",percentage=""),
            arrow=dict(value="",percentage=""),
            boo=dict(value="",percentage="")
            ),
        nickname=dict(
            value="",
            subpage_link= ""
        ),
        auther=dict(
            name=""
        )
    )

    page = browser.new_page()
    page.goto(targetPage)
    
    data_elements = page.query_selector('div[data-v-8f65c8fe]:not(.headline).mt-4').query_selector_all("div[data-v-8f65c8fe]")
    data_elements = data_elements[0:9]
    associate_link_elements = page.query_selector_all('a.e7-no-wrap.px-1')
    posts_comments_nickname_elements = []
    reaction_elements = []
    auther = targetPage.split("?")[0].split("/")[-1]
    overview_data['auther']['name'] = auther

    #抓取到的雜資料前置處理分類
    for de in data_elements:
        text = de.text_content()
        if "%" in text:
            reaction_elements.append(de)
        else:
            posts_comments_nickname_elements.append(de)

    # 取得相關子網頁的連結
    for ale in associate_link_elements:
        match ale.text_content():
            case "發文":
                overview_data["posts"]["subpage_link"] = configSetting.pttRootURL + ale.get_attribute("href")
            case "留言":
                overview_data["comments"]["subpage_link"] = configSetting.pttRootURL + ale.get_attribute("href")
            case "暱稱":
                overview_data["nickname"]["subpage_link"] = configSetting.pttRootURL + ale.get_attribute("href")
    # 處理互動
    for re in reaction_elements:
        text = str(re.text_content())
        res = regularExpression.search(re_pattern,text)
        # group 的匹配群組從1開始計數
        if "收到" in res.group(1) and "推" in res.group(1):
            overview_data["posts"]["thumb"]["value"] = res.group(2)
            overview_data["posts"]["thumb"]["percentage"] = res.group(3)
        elif "收到" in res.group(1) and "→" in res.group(1):
            overview_data["posts"]["arrow"]["value"] = res.group(2)
            overview_data["posts"]["arrow"]["percentage"] = res.group(3)
        elif "收到" in res.group(1) and "噓" in res.group(1):
            overview_data["posts"]["boo"]["value"] = res.group(2)
            overview_data["posts"]["boo"]["percentage"] = res.group(3)         
        elif "送出" in res.group(1) and "推" in res.group(1):
            overview_data["comments"]["thumb"]["value"] = res.group(2)
            overview_data["comments"]["thumb"]["percentage"] = res.group(3)
            overview_data["posts"]["boo"]["percentage"] = res.group(3)         
        elif "送出" in res.group(1) and "→" in res.group(1):
            overview_data["comments"]["arrow"]["value"] = res.group(2)
            overview_data["comments"]["arrow"]["percentage"] = res.group(3)
            overview_data["posts"]["boo"]["percentage"] = res.group(3)         
        elif "送出" in res.group(1) and "噓" in res.group(1):
            overview_data["comments"]["boo"]["value"] = res.group(2)
            overview_data["comments"]["boo"]["percentage"] = res.group(3)

    # 處理發文與留言
    for pcne in posts_comments_nickname_elements:
        text = str(pcne.text_content())
        res = regularExpression.search(pcne_pattern,text)
        if "發文" in res.group(1):
            overview_data["posts"]["value"] = res.group(2)
        elif "留言" in res.group(1):
            overview_data["comments"]["value"] = res.group(2)
        else:
            overview_data["nickname"]["value"] = res.group(2)

    page.close()
    return overview_data
            

