import discord
import os
import asyncio
from discord.ext import commands
import config
import config_token

TOKEN = config_token.TOKEN

config.RADIO_LIST = {}

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    for guild in bot.guilds:
        voice_client = guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            print(f"Отключился от голосового канала в {guild.name}")

def load_radio_list():
    radio_list = {}
    with open("radio_list.txt", "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.strip().split("=")
            radio_list[key] = value
    return radio_list


def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if filename != "__init__.py":
                bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    config.RADIO_LIST = load_radio_list()
    load()


if __name__ == "__main__":
    asyncio.run(main())
    print(config.RADIO_LIST)
    bot.run(TOKEN)