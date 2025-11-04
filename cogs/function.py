import discord
from discord.ext import commands


class Func(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embed(title, description=None):
        if description:
            embed = discord.Embed(title=title, description=description, color=0x2b2d31)
        else:
            embed = discord.Embed(title=title, color=0x2b2d31)
        return embed


def setup(bot):
    bot.add_cog(Func(bot))