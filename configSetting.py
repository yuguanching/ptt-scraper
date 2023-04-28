
import platform
from ioService import reader

os_type = ""
if "mac" in platform.platform():
    os_type = "mac"
else:
    os_type = "window"

json_array_data = reader.readInputJson()


pttRootURL = "https://pttweb.cc"
playwirght_headless = True

ipinfo_access_token = "c27c6dbcc7578d"

category_posts_timeline = "2023-04-20 00:00:00"

multithread_median = 10
multithread_high = 20

asyncio_patch_number = 20