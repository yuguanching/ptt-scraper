import re as regularExpression
import configSetting
import traceback
from bs4 import BeautifulSoup
from pprint import pprint
from playwright.sync_api import Browser
from scraper import common


class auther(common.paginationChecker):

    def parseOverviewData(self, targetPage: str, browser: Browser) -> dict:
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

        page = browser.new_page()
        page.goto(targetPage)

        data_elements = page.query_selector('div[data-v-8f65c8fe]:not(.headline).mt-4').query_selector_all("div[data-v-8f65c8fe]")
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

    def parsePostsLink(self, resp: str) -> list:
        posts_link_list = []
        soup = BeautifulSoup(resp, "html.parser")
        posts_block = soup.find_all("div", {'class': 'thread-item e7-container'})
        for pb in posts_block:
            link = configSetting.pttRootURL + str(pb.find("div", {'class': "e7-left"}).find("a").get("href"))
            posts_link_list.append(link)

        return posts_link_list

    def parsePostsData(self, resp: str, auther: str, targetURL: str) -> list:
        post_data_list = []
        soup = BeautifulSoup(resp, "html.parser")
        auther, nickname = "", ""
        article_content, network_data = "", ""
        ip, geosite = "", ""
        main_point_str = ""

        # 開始抓取需要的資料
        """
        post_id: 文章編號
        post_aid: 經過編碼轉換後的文章編號, 以#作為開頭
        title: 文章標題
        category: 看板分類
        auther: 作者
        nickname: 發此篇文所使用的暱稱
        create_time: 發文時間
        thumb: 推數
        arrow: 箭頭數
        boo: 噓數
        comment_number: 留言數
        comment_people: 留言實際參與人數
        article_content: 文章內容
        ip: 發文時所記錄的ip
        geosite: 發文時紀錄的地理位置
        """
        try:
            post_id = targetURL.split("/")[-1]
            post_aid = regularExpression.search(r"(.*?)\:\s(#[0-9a-zA-Z_-]+)\s\((.*?)\)",
                                                str(soup.find("div", {'class': 'my-2 e7-head-small'}).text)).group(2)
            title = str(soup.find("h1", {'class': 'title mt-2'}).text).strip()
            category = soup.find("span", {'class': 'e7-board-name-standalone'}).text
            board_point = soup.find("div", {'class': 'e7-grid-wrapper'})

            name_point_str = str(board_point.find('span', text="作者").find_next_sibling('span', {'class': 'e7-head-content'}).get_text())
            if '(' in name_point_str:
                auther, nickname = regularExpression.search(r"(.*?)\((.*?)\)", str(board_point.select('span')[4].get_text(strip=True))).groups()
            else:
                auther = name_point_str

            time_point_str = str(board_point.find('span', text="時間").find_next_sibling('span', {'class': 'e7-head-content'}).get_text())
            create_time = regularExpression.search(r"(.*?)\((.*?)\)", time_point_str).group(2)

            reaction_point_str = str(board_point.find('span', text="推噓").find_next_sibling('span', {'class': 'e7-head-content'}).get_text())
            reaction_tuple_str = str(regularExpression.search(r"(.*?)\((.*?)\)", reaction_point_str).group(2))
            thumb, boo, arrow = regularExpression.search(r"([0-9]+)推\s([0-9]+)噓\s([0-9]+)→", reaction_tuple_str).groups()

            comment_point_str = str(board_point.find('span', text="留言").find_next_sibling('span', {'class': 'e7-head-content'}).get_text())
            comment_number, comment_people = regularExpression.search(r"([0-9]+)則,\s([0-9]+)人參與", comment_point_str).groups()

            # 有可能沒有人和文章內容(有文章項目但沒有文章內文)
            main_points = soup.find("div", {'class': 'e7-main-text-area mb-5'}).find_all("div", attrs={'style': 'line-height:1.5;'})

            if len(main_points) > 0:
                # 存在文章的話, 將需要的內文區塊彙整串連
                for mp in main_points:
                    main_point_str += mp.text
                    # 避免抓到留言區的資料, 搜索到主內文中有--符號就跳出
                    if '--' in mp.text:
                        break
                main_content = main_point_str.strip().split("--")
                article_content = main_content[0].strip()
                network_data = main_content[-1].strip()

                if network_data != "":
                    ip = regularExpression.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", network_data)[0]
                    if len(regularExpression.findall(r"來自:\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\((.*?)\)", network_data)) >= 1:
                        geosite = regularExpression.findall(r"來自:\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\((.*?)\)", network_data)[0]
        except:
            print(f"error, {targetURL}, {traceback.format_exc()}")

        # 針對沒有取得地理位置的資料, 用外部套件以ip取得地理位置
        # if geosite == "":
        #     geosite = ipLookup.ipLookupByIPInfo(ip)

        post_data_dict = {
            "post_id": post_id,
            "post_aid": post_aid,
            "title": title,
            "category": category,
            "auther": auther,
            "nickname": nickname,
            "create_time": create_time,
            "thumb": int(thumb),
            "arrow": int(arrow),
            "boo": int(boo),
            "comment_number": int(comment_number),
            "comment_people": int(comment_people),
            "article_content": article_content,
            "ip": ip,
            "geosite": geosite,
            "post_url": targetURL
        }

        post_data_list.append(post_data_dict)
        return post_data_list

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

    def checkPages(self, targetType: str, targetPage: str, browser: Browser):

        print(f"檢查{targetType}的總頁數")

        pages_list = []
        pages_list.append(targetPage)
        tail_page_url = ""
        page_number = 0

        page = browser.new_page()
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
