import re
import requests
import ipinfo
import configSetting

from auther import nickname,posts,comments
from pprint import pprint
from ioService import parser

# a = "來自: 84.17.56.71 (香港)"
# ttt = "71則, 54人參與, 2天前最新"
# url = "https://www.pttweb.cc/bbs/Gossiping/M.1682575253.A.480"

# resp = requests.get(url)

# lll = posts.parsePostsData(resp.text,"asdf2004",url)

# pprint(lll)
# parser.buildCollectData(lll,"asdf2004")

ip_address = "209.58.188.40"

handler = ipinfo.getHandler(configSetting.ipinfo_access_token)
details = handler.getDetails(ip_address=ip_address)
print(details.all)