from datetime import datetime

import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from json import loads
from requests import get
from bot.plugins.pluginsConfig import *


@nonebot.scheduler.scheduled_job('cron', hour=NotificationTime['hour'], minute=NotificationTime['minute'])
async def _():
    bot = nonebot.get_bot()

    res = get(
        'https://temp.163.com/special/00804KVA/cm_yaowen20200213.js?callback=data_callback')
    text = '[' + res.content.decode('gbk')[15:-2] + ']'
    news_list = loads(text)
    news_message = ''
    for new in news_list[:10]:
        key_list = []
        for keyword in new['keywords']:
            key_list.append(keyword['keyname'])

        news_message += f"    {news_list.index(new) + 1}、{new['title']}\n         详情见：{new['docurl']}\n         关键词：{'、'.join(key_list)}\n"

    try:
        await bot.send_group_msg(group_id=NewsGroupID,
                                 message=news_message)
    except CQHttpError:
        pass
