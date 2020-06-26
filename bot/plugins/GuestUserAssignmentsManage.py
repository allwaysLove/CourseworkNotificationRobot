# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time  : 2020/4/15 11:07
# @Author: 韩家旭
# @File  : GuestUserAssignmentsManage.py

import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from json import loads
from requests import get
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


@on_command('发送有效作业', aliases=('发送作业', '有效作业', '作业'), permission=perm.EVERYBODY, only_to_me=True)
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
            await bot.send_private_msg(user_id=user_id, message='网络请求错误！请通知管理员！')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_private_msg(user_id=user_id, message='有效作业列表为空')
        except CQHttpError:
            pass
        return
    # 群消息：发送至群聊 并@ 发送方
    if group_id:
        try:
            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
    # 私聊消息：发送至 发送方
    elif user_id:
        try:
            await bot.send_private_msg(user_id=user_id, message=message)
        except CQHttpError:
            pass


@on_command('发送本周作业', aliases=('本周作业',), permission=perm.EVERYBODY, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    # bot = session.bot()
    user_id = session.event.user_id
    group_id = session.event.group_id
    this_week_start = datetime.now() - timedelta(days=datetime.now().weekday())

    assignments = f'【本周作业通知】\n（{this_week_start.strftime("%m.%d")}-{datetime.now().strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'week')

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
            await bot.send_private_msg(user_id=user_id, message='网络请求错误！请通知管理员！')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_private_msg(user_id=user_id, message='本周作业列表为空')
        except CQHttpError:
            pass
        return

    # 群消息：发送至群聊 并@ 发送方
    if group_id:
        try:
            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
    # 私聊消息：发送至 发送方
    elif user_id:
        try:
            await bot.send_private_msg(user_id=user_id, message=message)
        except CQHttpError:
            pass


@on_command('发送近期作业', aliases=('近期作业',), permission=perm.EVERYBODY, only_to_me=True)
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

    if float(days) < 1:
        message = '天数参数 非法，请重新发送命令，并输入合法的天数（大于等于 1）!'
        # 群消息：发送至群聊 并@ 发送方
        if group_id:
            try:
                await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
            except CQHttpError:
                pass
        # 私聊消息：发送至 发送方
        elif user_id:
            try:
                await bot.send_private_msg(user_id=user_id, message=message)
            except CQHttpError:
                pass
        return

    time_start = datetime.now()
    time_end = time_start + timedelta(days=int(days))

    assignments = f'【近{_to_chinese4(int(days))}天即将截止作业汇总】\n（{time_start.strftime("%m.%d")}-{time_end.strftime("%m.%d")}）\n'

    message = get_assignments(assignments, 'days', days=days)

    if '网络请求错误' in message:
        try:
            await bot.send_private_msg(user_id=AdministratorID, message='网络请求错误！请检查！')
            await bot.send_private_msg(user_id=user_id, message='网络请求错误！请通知管理员！')
        except CQHttpError:
            pass
        return
    elif not message:
        try:
            await bot.send_private_msg(user_id=user_id, message=f'近{_to_chinese4(days)}天即将截止作业列表为空')
        except CQHttpError:
            pass
        return

    # 群消息：发送至群聊 并@ 发送方
    if group_id:
        try:
            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
    # 私聊消息：发送至 发送方
    elif user_id:
        try:
            await bot.send_private_msg(user_id=user_id, message=message)
        except CQHttpError:
            pass


# 使用说明
@on_command('发送使用说明', aliases=('发送说明', '发送菜单', '使用说明', '说明', '菜单', ''), permission=perm.EVERYBODY, only_to_me=True)
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    # bot = session.bot()
    user_id = session.event.user_id
    group_id = session.event.group_id

    menu_choice_list = [
        '【打开本菜单】 \n        可以使用命令：“发送使用说明、发送说明、发送菜单、使用说明、说明、菜单”\n',
        '【获取所有未截止作业】 \n        可以使用命令：“发送有效作业、发送作业、有效作业、作业”\n',
        '【获取本周作业（包括：本周发布作业与本周即将截止作业）】 \n        可以使用命令：“发送本周作业、本周作业”\n',
        '【获取近期即将截止作业（可指定天数）】 可使用命令：“发送近期作业、近期作业”\n',
        '【注①】：使用命令必须在命令前加入该列表中任一命令控制符【 /, !, ／, ！】，（例如：/发送作业）',
        '【注②】：可以小窗私聊机器人发送命令，亦可在机器人所在群中 @机器人 发送命令（例如：@机器人 /发送作业）'
    ]

    message = '【使用说明】\n\n'
    for choice in menu_choice_list:
        message += f'    {menu_choice_list.index(choice) + 1}）{choice}\n'

    if user_id in bot.config.SUPERUSERS:
        message += '--------------------\n【管理员命令】：\n'
        super_user_menu = [
            '【通知作业（所有未截止作业）】\n        可以使用命令：“通知有效作业、通知作业”\n',
            '【通知本周作业】 \n        可以使用命令：“通知本周作业”\n',
            '【通知近期作业（近十天作业）】 \n        可以使用命令：“通知近期作业”'
        ]
        for choice in super_user_menu:
            message += f'    {super_user_menu.index(choice) + 1}）{choice}\n'

    # 群消息：发送至群聊 并@ 发送方
    if group_id:
        try:
            await bot.send_group_msg(group_id=group_id, message=message + f'[CQ:at,qq={user_id}]')
        except CQHttpError:
            pass
    # 私聊消息：发送至 发送方
    elif user_id:
        try:
            await bot.send_private_msg(user_id=user_id, message=message)
        except CQHttpError:
            pass
