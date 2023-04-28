
import os
import configSetting
from datetime import datetime


def checkDirAndCreate(targetName) -> None:
    if os.path.exists("./output/" + str(targetName)):
        print("subDir " + str(targetName) + " is already exists")
    else:
        os.mkdir("./output/" + str(targetName))
        os.makedirs("./output/" + str(targetName) + "/img/sharer")
        os.makedirs("./output/" + str(targetName) + "/img/been_sharer")
        os.makedirs("./output/" + str(targetName) + "/img/word_cloud")
        print("subDir " + str(targetName) + " created successfully")


def dateCompare(targetTimeStr) -> bool:
    target_time_obj = datetime.strptime(targetTimeStr, "%Y-%m-%d %H:%M:%S")
    user_set_time_obj = datetime.strptime(configSetting.category_posts_timeline, "%Y-%m-%d %H:%M:%S")

    if target_time_obj > user_set_time_obj:
        return True
    else:
        return False
