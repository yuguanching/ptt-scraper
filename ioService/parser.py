from operator import mod
import pandas as pd
import os
import traceback
import numpy
import json
import openpyxl
import configSetting

from collections import Counter
from ioService import writer


def buildCollectData(rawDataList, subDir, dropNA=False):

    excel_file = './output/' + subDir + '/collectData.xlsx'
    post_id = []
    post_aid = []
    title = []
    category = []
    auther = []
    nickname = []
    date = []
    thumb = []
    arrow = []
    boo = []
    comment_number = []
    comment_people = []
    article_content = []
    ip = []
    geosite= []
    post_url = []


    print(f"開始產生{subDir}的各項統計資料")
    # 各內容的抓取位置請參考__resolverEdgesPage__()
    for raw_data in rawDataList:
        
        post_id.append(raw_data['post_id'])
        post_aid.append(raw_data['post_aid'])
        title.append(raw_data['title'])
        category.append(raw_data['category'])
        auther.append(raw_data['auther'])
        nickname.append(raw_data['nickname'])
        date.append(raw_data['create_time'])
        thumb.append(raw_data['thumb'])
        arrow.append(raw_data['arrow'])
        boo.append(raw_data['boo'])
        comment_number.append(raw_data['comment_number'])
        comment_people.append(raw_data['comment_people'])
        article_content.append(raw_data['article_content'])
        ip.append(raw_data['ip'])
        geosite.append(raw_data['geosite'])
        post_url.append(raw_data['post_url'])


    df = pd.DataFrame({
        '文章編號':post_id,
        '文章aid代碼':post_aid,
        '標題':title,
        '分類':category,
        '作者':auther,
        '暱稱':nickname,
        '發文時間':date,
        '推文數':thumb,
        '噓文數':boo,
        '箭頭數':arrow,
        '留言數':comment_number,
        '留言實際參與人數':comment_people,
        '內文':article_content,
        'ip':ip,
        '地理位置':geosite,
        '文章網址':post_url
    })

    if dropNA:
        df['內文'].replace('', numpy.nan, inplace=True)
        df.dropna(subset=['內文'], inplace=True)
        df.reset_index(drop=True)

    writer.pdToExcel(des=excel_file, df=df, sheetName="collection", autoFitIsNeed=False)

    print(f"{subDir}的各項統計資料寫入完成")