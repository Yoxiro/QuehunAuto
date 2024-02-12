import asyncio
import os
import botpy
import yaml
from QQbot.QQbot import MyClient
from botpy.ext.cog_yaml import read

with open("config/config.yaml","rt") as f:
    QQconfig = yaml.load(f.read(), Loader=yaml.FullLoader)

intents = botpy.Intents(public_guild_messages=True)
client = MyClient(intents=intents)
client.run(appid=QQconfig["appid"], secret=QQconfig["secret"])