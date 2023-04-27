import requests
import re as regularExpression
from bs4 import BeautifulSoup
from pprint import pprint



def parseCommentsData(resp:str, auther:str)->list:
    comment_data_list = []
    soup = BeautifulSoup(resp,"html.parser")

    comment_block_elements = soup.find_all("div",{'class':'thread-item'})
    for cbe in comment_block_elements:
        post_id = str(cbe.find("a").get("href")).split("/")[-1]
        comment_content_elements = cbe.find_all("div",{'class','e7-top mt-2'})

        # 每篇文的留言逐條處理
        for cce in comment_content_elements:
            comment_type = cce.find("span",{'class':['f11','white--text']}).get_text()
            comment_content = cce.find("span",{'class':'yellow--text text--darken-2 e7-author'}).find_next_sibling("span").get_text()[1:]
            post_create_time = regularExpression.search(r"([0-9]+)/([0-9]+)/([0-9]+)\s([0-9]+):([0-9]+)",str(cbe.get_text())).groups()
            create_year = post_create_time[0]
            comment_create_data = str(cce.find("span",{'class':'ml-3 grey--text text--lighten-1'}).get_text())
            ip = ""
            comment_create_time = ""
            comment_create_data_arr = comment_create_data.split(" ")
            if len(comment_create_data_arr)>=3:
                ip = comment_create_data_arr[0]
                comment_create_time = create_year + "/" + comment_create_data_arr[1] + " " + comment_create_data_arr[2]
            else:
                comment_create_time = create_year + "/" + comment_create_data

            comment_data_dict = {
                "post_id":post_id,
                "auther": auther,
                "comment_create_time":comment_create_time,
                "comment_type":comment_type,
                "comment_content":comment_content,
                "ip":ip
            }
            
            comment_data_list.append(comment_data_dict)

    return comment_data_list