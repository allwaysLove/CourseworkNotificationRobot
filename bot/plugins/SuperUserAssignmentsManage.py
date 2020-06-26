# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2020/4/13 11:07
# @Author: 韩家旭
# @File  : SuperUserAssignmentsManage.py

import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from json import loads
from requests import get
from requests.exceptions import ConnectionError
from nonebot import on_command, CommandSession, permission as perm
from datetime import datetime, timedelta
from bot.plugins.pluginsConfig import *


def get_assignments(assignments, assignment_type, days=None):
    serial_num_list = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩', '⑪', '⑫', '⑬', '⑭', '⑮',
                       '⑯', '⑰', '⑱', '⑲', '⑳', '㉑', '㉒', '㉓', '㉔', '㉕', '㉖', '㉗', '㉘', '㉙', '㉚']
    if assignment_type == 'days':
        if not days:
            return '请输入正确 天数 参数！'
        else:
            url = f'http://127.0.0.1:8010/assignments/get_assignments/?assignment_type={assignment_type}&days={days}'
    else:
        url = f'http://127.0.0.1:8010/assignments/get_assignments/?assignment_type={assignment_type}'
    try:
        res = get(url)
    except ConnectionError:
        return '网络请求错误，请通知管理员检查！'
    if res.status_code == 404:
        return ''
    res_content = res.content.decode('utf-8')
    res_json = loads(res_content)
    # print(res_json)
    schedule_names = list(res_json.keys())

    # print(list(res_json.keys()))
    for key in schedule_names:
        print(schedule_names.index(key))
        assignments += f'\n{schedule_names.index(key) + 1}) {key}\n\n'
        assignment_list = res_json.get(key)
        for assignment in assignment_list:
            assignments += f'    {serial_num_list[assignment_list.index(assignment)]} {assignment}\n'

    print(assignments)
    return assignments


def _to_chinese4(num):
    _MAPPING = (
        u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'十一', u'十二', u'十三', u'十四', u'十五', u'十六',
        u'十七',
        u'十八', u'十九')
    _P0 = (u'', u'十', u'百', u'千',)
    _S4 = 10 ** 4
    assert (0 <= num and num < _S4)
    if num < 20:
        return _MAPPING[num]
    else:
        lst = []
        while num >= 10:
            lst.append(num % 10)
            num = num / 10
        lst.append(num)
        c = len(lst)  # 位数
        result = u''

        for idx, val in enumerate(lst):
            val = int(val)
            if val != 0:
                result += _P0[idx] + _MAPPING[val]
                if idx < c - 1 and lst[idx + 1] == 0:
                    result += u'零'
        return result[::-1]


@on_command('通知有效作业', aliases=('通知作业',), permission=perm.SUPERUSER, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    user_id = session.event.user_id
    group_id = session.event.group_id

    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    this_week_end = this_week_start + timedelta(days=5)
    start_study_day = datetime(*SemesterStartDate)

    week_count = int((this_week_start - start_study_day).days / 7 + 1)

    assignments = f'【第{_to_chinese4(week_count)}周作业汇总】\n（{this_week_start.strftime("%m.%d")}-{this_week_end.strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'all_effective')

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
        except CQHttpError:
            pass
        return

    elif not message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='有效作业列表为空')
        except CQHttpError:
            pass
        return

    # 私聊消息：发送至 通知群
    if not group_id:
        try:
            # 班级通知群群号 NotificationGroupID
            await bot.send_group_msg(group_id=NotificationGroupID, message=message)
        except CQHttpError:
            pass


@on_command('通知本周作业', permission=perm.SUPERUSER, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    group_id = session.event.group_id
    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())

    assignments = f'【本周作业通知】\n（{this_week_start.strftime("%m.%d")}-{datetime.now().strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'week')

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='本周作业列表为空')
        except CQHttpError:
            pass
        return

    # 私聊消息：发送至 通知群
    if not group_id:
        try:
            # 班级通知群群号 NotificationGroupID
            await bot.send_group_msg(group_id=NotificationGroupID, message=message)
        except CQHttpError:
            pass


@on_command('通知近期作业', permission=perm.SUPERUSER, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    group_id = session.event.group_id
    time_start = datetime.now()
    time_end = time_start + timedelta(days=10)

    assignments = f'【近十天即将截止作业汇总】\n（{time_start.strftime("%m.%d")}-{time_end.strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'days', days=10)

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='近十天即将截止作业列表为空')
        except CQHttpError:
            pass
        return

    # 私聊消息：发送至 通知群
    if not group_id:
        try:
            # 班级通知群群号 NotificationGroupID
            await bot.send_group_msg(group_id=NotificationGroupID, message=message)
        except CQHttpError:
            pass


# 每日 当天即将截止作业提醒
@nonebot.scheduler.scheduled_job('cron', hour=NotificationTime['hour'], minute=NotificationTime['minute'])
async def _():
    bot = nonebot.get_bot()
    time_start = datetime.now()
    time_end = time_start + timedelta(days=1)

    assignments = f'【今天即将截止作业汇总】\n（{time_start.strftime("%m.%d")}-{time_end.strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'days', days=1)

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
        except CQHttpError:
            pass
        return
    elif not message:
        return

    # 定时群消息：发送至 通知群
    try:
        # 班级通知群群号 NotificationGroupID
        await bot.send_group_msg(group_id=NotificationGroupID, message=message)
    except CQHttpError:
        pass

if __name__ == '__main__':
    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    this_week_end = this_week_start + timedelta(days=5)
    start_study_day = datetime(2020, 2, 17)

    week_count = int((this_week_start - start_study_day).days / 7 + 1)

    assignments = f'【第{_to_chinese4(week_count)}周作业汇总】\n（{this_week_start.strftime("%m.%d")}-{this_week_end.strftime("%m.%d")}）\n'
    # assignments = f'【作业通知】\n（{this_week_start.strftime("%m.%d")}-{datetime.now().strftime("%m.%d")}）\n'
    assignments = get_assignments(assignments, 'all_effective')

    print(assignments)
