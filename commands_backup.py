import discord
from discord.ext import commands
import config
import random

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


async def _get_station_list(ctx: discord.AutocompleteContext):
    try:
        query = str(ctx.options['station']).strip().lower()
        results = {}
        for key, value in config.RADIO_LIST.items():
            if query in key.lower():
                results[key] = value
                if len(results) >= 25:
                    break
        return results
    except Exception as e:
        print(f"Ошибка в автозаполнении: {e}")
        return []


async def _connect(ctx):
    if ctx.user.voice and ctx.user.voice.channel:
        channel = ctx.user.voice.channel
        await channel.connect()
        return True
    else:
        await ctx.respond("Сначала зайдите в голосовой канал!", ephemeral=True)
        return False


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_url = None
        self.voice_client = None
        self.is_paused = False

    @discord.slash_command(name="play", description="Включить радио")
    async def play_radio(
            self,
            ctx: discord.ApplicationContext,
            station: discord.Option(str, autocomplete=_get_station_list,
                                    description="Выберите радиостанцию для воспроизведения")
    ):
        self.current_url = config.RADIO_LIST.get(station)

        if self.current_url is None:
            await ctx.respond("Станция не найдена", ephemeral=True)
            return

        voice_client = ctx.guild.voice_client
        if not voice_client:
            connected = await _connect(ctx)
            if not connected:
                return
            voice_client = ctx.guild.voice_client

        source = discord.FFmpegPCMAudio(self.current_url, **FFMPEG_OPTIONS)
        voice_client.play(source)
        play_msg = random.choice(config.PLAY_RESPONSES)
        await ctx.respond(play_msg + station)

    @commands.slash_command(name="pause", description="Поставить на паузу или продолжить воспроизведение")
    async def pause_radio(self, ctx: discord.ApplicationContext):
        voice_client = ctx.guild.voice_client
        if not voice_client or not voice_client.is_playing():
            await ctx.respond("Сейчас ничего не воспроизводится", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.pause()
            await ctx.respond("Пауза")
        elif voice_client.is_paused():
            voice_client.resume()
            await ctx.respond("Продолжаем")
        else:
            await ctx.respond("Сейчас ничего не воспроизводится", ephemeral=True)

    @commands.slash_command(name="leave", description="Выйти из голосового канала")
    async def leave_radio(self, ctx: discord.ApplicationContext):
        voice_client = ctx.guild.voice_client
        if voice_client is None:
            await ctx.respond("Меня и так здесь нет", ephemeral=True)
            return
        await voice_client.disconnect()
        leave_msg = random.choice(config.LEAVE_RESPONSES)
        await ctx.respond(leave_msg)

    @commands.slash_command(name="summon", description="Зайти в голосовой канал")
    async def summon(self, ctx: discord.ApplicationContext,
                     channel: discord.Option(discord.VoiceChannel, description="Выберите канал")):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.respond(f"Бот подключён к голосовому каналу: {channel.name}")


def setup(bot):
    bot.add_cog(Radio(bot))
