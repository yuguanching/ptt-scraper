import re as regularExpression
import configSetting
import traceback
from webManager import customPlayWright
from bs4 import BeautifulSoup
from pprint import pprint
from scraper import common


class auther(common.paginationChecker, common.postsScraper):

    def parseOverviewData(self, targetPage: str) -> dict:
        overview_data = dict(
            posts=dict(
                value="",
                subpage_link="",
                thumb=dict(value="", percentage=""),
                arrow=dict(value="", percentage=""),
                boo=dict(value="", percentage="")
            ),
            comments=dict(
                value="",
                subpage_link="",
                thumb=dict(value="", percentage=""),
                arrow=dict(value="", percentage=""),
                boo=dict(value="", percentage="")
            ),
            nickname=dict(
                value="",
                subpage_link=""
            ),
            auther=dict(
                name=""
            )
        )

        page = customPlayWright.browser_manager.browser.new_page()
        page.goto(targetPage)

        data_elements = page.query_selector_all('div[data-v-8f65c8fe]:not(.headline).mt-4 >> div[data-v-8f65c8fe]')
        data_elements = data_elements[0:9]
        associate_link_elements = page.query_selector_all('a.e7-no-wrap.px-1')
        posts_comments_nickname_elements = []
        reaction_elements = []
        auther = targetPage.split("?")[0].split("/")[-1]
        overview_data['auther']['name'] = auther

        # 抓取到的雜資料前置處理分類
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
            res = regularExpression.search(r"(.*?) ([0-9]+?) \((.*?)%\)", text)
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
            res = regularExpression.search(r"(.*?)\: ([0-9]+)", text)
            if "發文" in res.group(1):
                overview_data["posts"]["value"] = res.group(2)
            elif "留言" in res.group(1):
                overview_data["comments"]["value"] = res.group(2)
            else:
                overview_data["nickname"]["value"] = res.group(2)

        page.close()
        return overview_data

    def parseCommentsData(self, resp: str, auther: str) -> list:
        comment_data_list = []
        soup = BeautifulSoup(resp, "html.parser")

        comment_block_elements = soup.find_all("div", {'class': 'thread-item'})
        for cbe in comment_block_elements:
            post_id = str(cbe.find("a").get("href")).split("/")[-1]
            comment_content_elements = cbe.find_all("div", {'class', 'e7-top mt-2'})

            # 每篇文的留言逐條處理
            for cce in comment_content_elements:
                comment_type = cce.find("span", {'class': ['f11', 'white--text']}).get_text()
                comment_content = cce.find("span", {'class': 'yellow--text text--darken-2 e7-author'}).find_next_sibling("span").get_text()[1:]
                post_create_time = regularExpression.search(r"([0-9]+)/([0-9]+)/([0-9]+)\s([0-9]+):([0-9]+)", str(cbe.get_text())).groups()
                create_year = post_create_time[0]
                comment_create_data = str(cce.find("span", {'class': 'ml-3 grey--text text--lighten-1'}).get_text())
                ip = ""
                comment_create_time = ""
                comment_create_data_arr = comment_create_data.split(" ")
                if len(comment_create_data_arr) >= 3:
                    ip = comment_create_data_arr[0]
                    comment_create_time = create_year + "/" + comment_create_data_arr[1] + " " + comment_create_data_arr[2]
                else:
                    comment_create_time = create_year + "/" + comment_create_data

                comment_data_dict = {
                    "post_id": post_id,
                    "auther": auther,
                    "comment_create_time": comment_create_time,
                    "comment_type": comment_type,
                    "comment_content": comment_content,
                    "ip": ip
                }

                comment_data_list.append(comment_data_dict)

        return comment_data_list

    # nickname 不需要點進去個別處理, 故僅有一層
    def parseNicknameData(self, resp: str, auther: str) -> list:
        nickname_data_list = []
        soup = BeautifulSoup(resp, "html.parser")

        # 開始抓取需要的資料
        """
        nickname: 暱稱
        post_number: 該暱稱所發過的文章數量
        """

        full_nickname_block = soup.find("div", {'class': 'e7-wrapper-nickname-full'})
        sub_nickname_blocks = full_nickname_block.find_all("div", {'class': ['e7-box', 'mb-4']})
        for nickname_data in sub_nickname_blocks:
            nickname = nickname_data.find("span", {'class': 'yellow--text'}).text
            post_tag_text = nickname_data.find("span", string=regularExpression.compile(r".*?文章數量.*?")).find_parent("div").text
            post_number = regularExpression.search(r"(.*?)：([0-9]+)", str(post_tag_text)).group(2)
            nickname_dict = dict(
                nickname=nickname,
                post_number=int(post_number),
                auther=auther
            )
            nickname_data_list.append(nickname_dict)

        return nickname_data_list

    def checkPages(self, targetType: str, targetPage: str):

        print(f"檢查{targetType}的總頁數")

        pages_list = []
        pages_list.append(targetPage)
        tail_page_url = ""
        page_number = 0

        page = customPlayWright.browser_manager.browser.new_page()
        page.goto(targetPage)

        tail_point_element = page.query_selector("a[data-v-c841833e]:has-text('尾頁')")

        if tail_point_element is not None:
            tail_page_url = str(tail_point_element.get_attribute("href"))
            res = regularExpression.search(r"(.*?)\=([0-9]+)", tail_page_url)
            page_number = int(res.group(2))
            for i in range(1, page_number+1):
                pages_list.append(targetPage + f"&page={i}")

        print(f"檢查完成, {targetType}共有{page_number+1}個分頁")
        page.close()
        return pages_list
