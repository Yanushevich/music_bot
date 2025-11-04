import discord
from discord.ext import commands
import config
import random

class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_url = None
        self.voice_client = None
        self.is_paused = False

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

    async def _connect(self, ctx, channel):
        if not channel:
            await ctx.respond("Вы должны быть в голосовом канале", ephemeral=True)
            return None
        voice_client = await channel.connect()
        return voice_client

    async def play(self, ctx, url, station):
        self.current_url = url
        if not ctx.guild.voice_client:
            self.voice_client = await self._connect(ctx, ctx.author.voice.channel)
            if self.voice_client is None:
                return
        else:
            self.voice_client = ctx.guild.voice_client
            if self.voice_client.is_playing():
                self.voice_client.stop()

        source = discord.FFmpegPCMAudio(url, **config.FFMPEG_OPTIONS)
        self.voice_client.play(source)
        play_msg = random.choice(config.PLAY_RESPONSES)
        await ctx.respond(play_msg + station)

    @commands.slash_command(name="play", description="Воспроизвести радиостанцию")
    async def play_radio(
            self,
            ctx: discord.ApplicationContext,
            station: discord.Option(str, autocomplete=_get_station_list, description="Выберите станцию")):
        url = config.RADIO_LIST.get(station)
        if not url:
            await ctx.respond("Станция не найдена", ephemeral=True)
            return
        await self.play(ctx, url, station)


    @commands.slash_command(name="pause", description="Поставить на паузу или продолжить воспроизведение")
    async def pause_radio(self, ctx: discord.ApplicationContext):
        voice_client = ctx.guild.voice_client
        if not voice_client or (not voice_client.is_playing() and not voice_client.is_paused()):
            await ctx.respond("Сейчас ничего не воспроизводится", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.pause()
            self.is_paused = True
            await ctx.respond("Пауза")
        elif voice_client.is_paused():
            voice_client.resume()
            self.is_paused = False
            await ctx.respond("Продолжаем")

    @commands.slash_command(name="leave", description="Выйти из голосового канала")
    async def leave_radio(self, ctx: discord.ApplicationContext):
        if self.voice_client is None:
            await ctx.respond("Меня и так здесь нет", ephemeral=True)
            return
        await self.voice_client.disconnect()
        leave_msg = random.choice(config.LEAVE_RESPONSES)
        await ctx.respond(leave_msg)

    @commands.slash_command(name="summon", description="Зайти в голосовой канал")
    async def summon(self, ctx: discord.ApplicationContext, channel: discord.Option(discord.VoiceChannel, description="Выберите канал")):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.move_to(channel)
        else:
            await self._connect(ctx, channel)
        await ctx.respond(f"Бот подключён к голосовому каналу: {channel.name}")

def setup(bot):
    bot.add_cog(Radio(bot))
