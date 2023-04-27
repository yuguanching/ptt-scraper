import requests
import re as regularExpression
from bs4 import BeautifulSoup


# nickname 不需要點進去個別處理, 故僅有一層
def parseNicknameData(resp:str, auther:str)->list:
    nickname_data_list = []
    soup = BeautifulSoup(resp,"html.parser")

    # 開始抓取需要的資料
    """
    nickname: 暱稱
    post_number: 該暱稱所發過的文章數量
    """

    full_nickname_block = soup.find("div",{'class':'e7-wrapper-nickname-full'})
    sub_nickname_blocks = full_nickname_block.find_all("div",{'class':['e7-box','mb-4']})
    for nickname_data in sub_nickname_blocks:
        nickname = nickname_data.find("span",{'class':'yellow--text'}).text
        post_tag_text = nickname_data.find("span",string=regularExpression.compile(r".*?文章數量.*?")).find_parent("div").text
        post_number = regularExpression.search(r"(.*?)：([0-9]+)",str(post_tag_text)).group(2)
        nickname_dict = dict(nickname=nickname,post_number=post_number,auther=auther)
        nickname_data_list.append(nickname_dict)

    return nickname_data_list