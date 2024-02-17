# -*- coding: utf-8 -*-
import asyncio
import os
import random

import botpy
from botpy import logging, Intents
from botpy.ext.cog_yaml import read
from botpy.message import Message
from QQbot.OCR import Ocr
from QQbot import FeishuAccess

from datetime import date
_log = logging.get_logger()


def FormingSentence(paiming) -> str:
    sentence = ""
    for i in range(0, 8, 2):
        part = paiming[i] + ":" + paiming[i + 1] + "\n"
        sentence = sentence + part
    return sentence

class MyClient(botpy.Client):
    def __init__(self, intents: Intents):
        super().__init__(intents)
        self.ocr = Ocr()
        self.feishuaccess = FeishuAccess.FeishuAccess()

    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        _log.info(message.author.avatar)
        if "sleep" in message.content:
            await asyncio.sleep(10)
        _log.info(message.author.username)

        if "/登记排名" in message.content:
            url = [item.url for item in message.attachments][0]
            await message.reply(content=f"识别时间可能较长，请稍作等待")
            self.ocr.get_url(url)
            paiming = self.ocr.detect()
            Tobesay = FormingSentence(paiming)
            await message.reply(content=Tobesay+"正在录入")
            self.feishuaccess.value_put_score(paiming)
            await message.reply(content=f"Done!")

        elif "/登记大牌" in message.content:
            url = [item.url for item in message.attachments][0]
            await message.reply(content=f"识别时间可能较长，请稍作等待")
            self.ocr.get_url(url)
            competitor_and_luck = self.ocr.paiyun()
            await message.reply(content=str(competitor_and_luck[0])+"总牌运点:"+str(competitor_and_luck[1]))
            self.feishuaccess.value_put_luck(competitor_and_luck)
            await message.reply(content = f"Done!")
        elif "/今日日期" in message.content:
            await message.reply(content = str(date.today()))
        elif "/唤醒机器人" in message.content:
            x = random.randint(1,3)
            if x == 1:
                await message.reply(content = "你好")
            elif x == 2:
                await message.reply(content = "你好吗")
            elif x == 3:
                await message.reply(content = "你没事吧")
        else:
            await message.reply(content = f"未能识别的指令，请重试或联系管理员@游子桀")


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True
    test_config = read(os.path.join(os.path.dirname(__file__), "../config/config.yaml"))
    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])