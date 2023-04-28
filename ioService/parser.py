from operator import mod
import pandas as pd
import os
import traceback
import numpy
import json
import openpyxl
import configSetting

from abc import ABC, abstractmethod
from collections import Counter
from ioService import writer


class dataSetBuilder(ABC):
    @abstractmethod
    def buildDataSet(self, rawDataList: list, subDir: str, mode: str, dropNA: bool):
        """抽象方法,待定義取得爬蟲資訊的手法."""
        pass


class postsDataBuilder(dataSetBuilder):
    def buildDataSet(self, rawDataList, subDir, mode, dropNA=False):

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
        geosite = []
        post_url = []

        print(f"開始產生{subDir}的文章統計資料")
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
            '文章編號': post_id,
            '文章aid代碼': post_aid,
            '標題': title,
            '分類': category,
            '作者': auther,
            '暱稱': nickname,
            '發文時間': date,
            '推文數': thumb,
            '噓文數': boo,
            '箭頭數': arrow,
            '留言數': comment_number,
            '留言實際參與人數': comment_people,
            '內文': article_content,
            'ip': ip,
            '地理位置': geosite,
            '文章網址': post_url
        })

        if dropNA:
            df['內文'].replace('', numpy.nan, inplace=True)
            df.dropna(subset=['內文'], inplace=True)
            df.reset_index(drop=True)

        writer.pdToExcel(des=excel_file, df=df, mode=mode, sheetName="posts", autoFitIsNeed=False)

        print(f"{subDir}的文章統計資料寫入完成")


class commentsDataBuilder(dataSetBuilder):
    def buildDataSet(self, rawDataList, subDir, mode, dropNA=False):

        excel_file = './output/' + subDir + '/collectData.xlsx'
        post_id = []
        auther = []
        comment_create_time = []
        comment_type = []
        comment_content = []
        ip = []

        print(f"開始產生{subDir}的留言統計資料")
        # 各內容的抓取位置請參考__resolverEdgesPage__()
        for raw_data in rawDataList:

            post_id.append(raw_data['post_id'])
            auther.append(raw_data['auther'])
            comment_create_time.append(raw_data['comment_create_time'])
            comment_type.append(raw_data['comment_type'])
            comment_content.append(raw_data['comment_content'])
            ip.append(raw_data['ip'])

        df = pd.DataFrame({
            '所屬文章編號': post_id,
            '作者': auther,
            '留言時間': comment_create_time,
            '留言類型': comment_type,
            '留言內容': comment_content,
            'ip': ip
        })

        if dropNA:
            df['留言內容'].replace('', numpy.nan, inplace=True)
            df.dropna(subset=['留言內容'], inplace=True)
            df.reset_index(drop=True)

        writer.pdToExcel(des=excel_file, df=df, mode=mode, sheetName="comments", autoFitIsNeed=False)

        print(f"{subDir}的留言統計資料寫入完成")


class nicknameDataBuilder(dataSetBuilder):
    def buildDataSet(self, rawDataList, subDir, mode, dropNA=False):

        excel_file = './output/' + subDir + '/collectData.xlsx'
        nickname = []
        post_number = []
        auther = []

        print(f"開始產生{subDir}的暱稱統計資料")
        # 各內容的抓取位置請參考__resolverEdgesPage__()
        for raw_data in rawDataList:

            nickname.append(raw_data['nickname'])
            auther.append(raw_data['auther'])
            post_number.append(raw_data['post_number'])

        df = pd.DataFrame({
            '暱稱': nickname,
            '作者': auther,
            '發過的文章數量': post_number
        })

        writer.pdToExcel(des=excel_file, df=df, mode=mode, sheetName="nickname", autoFitIsNeed=False)

        print(f"{subDir}的暱稱統計資料寫入完成")


class autherDataBuilder():
    def __init__(self):
        self.postsBuilder = postsDataBuilder()
        self.commentsBuilder = commentsDataBuilder()
        self.nicknameBuilder = nicknameDataBuilder()
