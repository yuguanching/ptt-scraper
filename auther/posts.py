import requests
import re as regularExpression
import configSetting
import traceback
from tool import ipLookup
from bs4 import BeautifulSoup




def parsePostsLink(resp:str)->list:
    posts_link_list = []
    soup = BeautifulSoup(resp,"html.parser")
    posts_block = soup.find_all("div",{'class':'thread-item e7-container'})
    for pb in posts_block:
        link = configSetting.pttRootURL + str(pb.find("div",{'class':"e7-left"}).find("a").get("href"))
        posts_link_list.append(link)

    return posts_link_list

def parsePostsData(resp:str, auther:str, targetURL:str)->list:
    post_data_list = []
    soup = BeautifulSoup(resp,"html.parser")
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
        post_aid = regularExpression.search(r"(.*?)\:\s(#[0-9a-zA-Z_-]+)\s\((.*?)\)",str(soup.find("div",{'class':'my-2 e7-head-small'}).text)).group(2)
        title = str(soup.find("h1",{'class':'title mt-2'}).text).strip()
        category = soup.find("span",{'class':'e7-board-name-standalone'}).text
        board_point = soup.find("div",{'class':'e7-grid-wrapper'})
        
        name_point_str = str(board_point.find('span',text="作者").find_next_sibling('span',{'class':'e7-head-content'}).get_text())
        if '(' in name_point_str:
            auther, nickname = regularExpression.search(r"(.*?)\((.*?)\)", str(board_point.select('span')[4].get_text(strip=True))).groups()
        else :
            auther = name_point_str
        
        time_point_str = str(board_point.find('span',text="時間").find_next_sibling('span',{'class':'e7-head-content'}).get_text())
        create_time = regularExpression.search(r"(.*?)\((.*?)\)", time_point_str).group(2)
        
        reaction_point_str = str(board_point.find('span',text="推噓").find_next_sibling('span',{'class':'e7-head-content'}).get_text())
        reaction_tuple_str = str(regularExpression.search(r"(.*?)\((.*?)\)",reaction_point_str).group(2))
        thumb, boo, arrow = regularExpression.search(r"([0-9]+)推\s([0-9]+)噓\s([0-9]+)→", reaction_tuple_str).groups()

        comment_point_str = str(board_point.find('span',text="留言").find_next_sibling('span',{'class':'e7-head-content'}).get_text())
        comment_number, comment_people = regularExpression.search(r"([0-9]+)則,\s([0-9]+)人參與", comment_point_str).groups()
        
        # 有可能沒有人和文章內容(有文章項目但沒有文章內文)
        main_points = soup.find("div",{'class':'e7-main-text-area mb-5'}).find_all("div",attrs={'style':'line-height:1.5;'})

        if len(main_points)>0:
            # 存在文章的話, 將需要的內文區塊彙整串連
            for mp in main_points:
                main_point_str += mp.text
                # 避免抓到留言區的資料, 搜索到主內文中有--符號就跳出
                if '--' in mp.text:
                    break
            main_content = main_point_str.strip().split("--")
            article_content = main_content[0].strip()
            network_data = main_content[-1].strip()

            if network_data!="":
                ip = regularExpression.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",network_data)[0]
                if len(regularExpression.findall(r"來自:\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\((.*?)\)",network_data))>=1:
                    geosite = regularExpression.findall(r"來自:\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\((.*?)\)",network_data)[0]
    except :
        print(f"error, {targetURL}, {traceback.format_exc()}")

    # 針對沒有取得地理位置的資料, 用外部套件以ip取得地理位置
    if geosite == "":
        geosite = ipLookup.ipLookupByIPInfo(ip)

    post_data_dict = {
        "post_id":post_id,
        "post_aid":post_aid,
        "title":title,
        "category":category,
        "auther":auther,
        "nickname":nickname,
        "create_time":create_time,
        "thumb":int(thumb),
        "arrow":int(arrow),
        "boo":int(boo),
        "comment_number":int(comment_number),
        "comment_people":int(comment_people),
        "article_content":article_content,
        "ip":ip,
        "geosite":geosite,
        "post_url":targetURL
    }

    post_data_list.append(post_data_dict)
    return post_data_list

