import random
import re

from nonebot import export, on_regex
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.params import Depends
from httpx import AsyncClient
from src.utils.content_check import content_check
from src.utils.log import logger
from tortoise import os
from src.plugins.roll.data import drinks_list

img_dir = os.path.realpath(__file__ + "/../img/")

Export = export()
Export.plugin_name = "掷筹"
Export.plugin_command = "掷筹 吃什么 喝什么"
Export.plugin_usage = "选择困难症的救星"
Export.default_status = True

what_to_eat = on_regex(r"^吃什么$", permission=GROUP, priority=5, block=True)
what_to_drinks = on_regex(r"^喝什么$", permission=GROUP, priority=5, block=True)
roll = on_regex(r"^(掷筹.+?)$", permission=GROUP, priority=5, block=True)


def get_content(event: GroupMessageEvent) -> str:
    '''从前置这些可前可后的消息中获取name'''
    text = event.get_plaintext()
    text_list = text.split()
    if len(text_list) == 2 and re.search(r"\d+-\d+", text_list[-1]):
        if len(text_list[-1]) > 20:
            return False, "数字太大我不认识！"
        try:
            start, end = text_list[-1].split("-")
            start, end = int(start), int(end)
            if end < start:
                start, end = end, start
            return True, [random.randint(start, end)]
        except:
            return False, "你要写自然数，自然数，知道不？"
    if len(text_list) < 2:
        return False, "正确格式是：“掷筹 甲 乙 丙 丁”"
    content_len = len(text_list[-1])
    if content_len > 512:
        return False, "你别写写么多啊！"
    if not content_check(text_list[-1]):
        return False, "写的内容不太文雅啊，重写一下吧！"
    return True, text_list[1:]


@what_to_eat.handle()
async def _(event: GroupMessageEvent):
    '''吃什么'''
    user_id = event.user_id
    group_id = event.group_id
    logger.debug(f"群{group_id} | {user_id} | 吃什么")
    client = AsyncClient()
    url = "https://www.ermaozi.cn/api/source/food/3"
    req = await client.get(url=url)
    req_data = req.json()
    if req_data.get("code") == 200:
        msg = "给你挑了这三个吃的："
        num = 0
        for i in random.sample(req_data.get("data"), k=3):
            num += 1
            msg += f"\n{num}.{i}"
        await what_to_eat.finish(msg)


@what_to_drinks.handle()
async def _(event: GroupMessageEvent):
    '''喝什么'''
    user_id = event.user_id
    group_id = event.group_id
    logger.info(
        f"<y>群{group_id}</y> | <g>{user_id}</g> | 喝什么"
    )
    msg = "给你挑了这三个喝的："
    num = 0
    for i in random.choices(drinks_list, k=3):
        num += 1
        msg += f"\n{num}.{i}"
    await what_to_drinks.finish(msg)


@roll.handle()
async def _(event: GroupMessageEvent, res=Depends(get_content)):
    '''掷筹'''
    user_id = event.user_id
    group_id = event.group_id
    result, content = res
    logger.debug(f"群{group_id} | {user_id} | 掷筹 | {content}")
    if not result:
        await roll.finish(content)
    msg = f"掷筹结果：【{random.choice(content)}】"
    logger.debug(f"群{group_id} | {user_id} | 结果 | {msg}")
    await roll.finish(msg)
