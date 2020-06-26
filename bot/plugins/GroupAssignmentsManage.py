# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2020/4/15 12:03
# @Author: 韩家旭
# @File  : GroupAssignmentsManage.py

import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from json import loads
from requests import get
from requests.exceptions import ConnectionError
from nonebot import on_command, CommandSession, permission as perm
from datetime import datetime, timedelta
from bot.plugins.pluginsConfig import *


# 获取作业信息
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


# 数字转序号
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


@on_command('发送有效作业', aliases=('发送作业',), permission=perm.IS_GROUP_MEMBER, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    group_id = session.event.group_id
    user_id = session.event.user_id

    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    this_week_end = this_week_start + timedelta(days=5)
    start_study_day = datetime(*SemesterStartDate)

    week_count = int((this_week_start - start_study_day).days / 7 + 1)

    assignments = f'【第{_to_chinese4(week_count)}周作业汇总】\n（{this_week_start.strftime("%m.%d")}-{this_week_end.strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'all_effective')
    print('测试：发送有效作业!')
    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
            await bot.send_group_msg(group_id=group_id, message='网络请求错误！请通知管理员！' + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            print('!@!@!@!@!@!@!@!@!@!@!@!@')
            print('发送群消息！')
            print('!@!@!@!@!@!@!@!@!@!@!@!@')

            await bot.send_group_msg(group_id=group_id, message='有效作业列表为空' + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
        return

    # 群私聊消息：发送至 发送方
    if group_id:
        try:
            print('!@!@!@!@!@!@!@!@!@!@!@!@')
            print('发送群消息！')
            print('!@!@!@!@!@!@!@!@!@!@!@!@')

            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass


@on_command('发送本周作业', aliases=('本周作业',), permission=perm.EVERYBODY, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    # bot = session.bot()
    group_id = session.event.group_id
    user_id = session.event.user_id
    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())

    assignments = f'【作业通知】\n（{this_week_start.strftime("%m.%d")}-{datetime.now().strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'week')

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
            await bot.send_group_msg(group_id=group_id, message='网络请求错误！请通知管理员！' + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_group_msg(group_id=group_id, message='本周作业列表为空' + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
        return

    # 群消息：发送至 发送方
    if group_id:
        try:
            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass


@on_command('发送近期作业', permission=perm.EVERYBODY, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    user_id = session.event.user_id
    group_id = session.event.group_id

    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将 days 参数跟在命令名后面，作为参数传入
            session.state['days'] = stripped_arg

    days = session.get('days', prompt='你想查询几天内截止的作业呢？')

    time_start = datetime.now()
    time_end = time_start + timedelta(days=int(days))

    assignments = f'【近{_to_chinese4(int(days))}天即将截止作业汇总】\n（{time_start.strftime("%m.%d")}-{time_end.strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'days', days=days)

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
            await bot.send_group_msg(group_id=group_id, message='网络请求错误！请通知管理员！' + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_group_msg(group_id=group_id, message=f'近{_to_chinese4(days)}天即将截止作业列表为空' + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
        return

    # 群消息：发送至 发送方
    if group_id:
        try:
            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
