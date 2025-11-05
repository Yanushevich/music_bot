import discord
import os
import asyncio
import config
import config_token
import cogs.commands

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


def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            if filename != "__init__.py":
                bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    config.RADIO_LIST = cogs.commands.load_radio_list()
    load()


if __name__ == "__main__":
    asyncio.run(main())
    bot.run(TOKEN)