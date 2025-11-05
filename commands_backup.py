import discord
from discord.ext import commands
import config
import random


def load_radio_list():
    radio_list = {}
    with open("radio_list.txt", "r", encoding="utf-8") as f:
        for line in f:
            key, value = line.strip().split("=")
            radio_list[key] = value
    return radio_list


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

    async def _disconnect_all(self, guild):
        for vc in self.bot.voice_clients:
            if vc.guild == guild:
                print(f"Отключаю голосовое соединение в гильдии {guild.id}")
                await vc.disconnect()
        print("Очистка соединений завершена")

    async def _connect(self, ctx):
        try:
            await self._disconnect_all(ctx.guild)
            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.respond("Вы должны быть в голосовом канале", ephemeral=True)
                return None
            self.voice_client = await ctx.author.voice.channel.connect(timeout=5, reconnect=True)
            return self.voice_client
        except Exception as e:
            err = f"Ошибка подключения: {e}"
            print(err)
            await ctx.respond(err)
            return None

    async def play(self, ctx, url, station):
        try:
            self.current_url = url
            if not ctx.guild.voice_client:
                self.voice_client = await self._connect(ctx)
                if self.voice_client is None:
                    await ctx.respond("Не удалось подключиться к голосовому каналу.")
                    return
            else:
                self.voice_client = ctx.guild.voice_client
                if self.voice_client.is_playing():
                    self.voice_client.stop()

            source = discord.FFmpegPCMAudio(url, **config.FFMPEG_OPTIONS)
            self.voice_client.play(source)
            play_msg = random.choice(config.PLAY_RESPONSES)
            await ctx.respond(play_msg + station)
        except Exception as e:
            err = f"Ошибка подключения: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="play", description="Воспроизвести радиостанцию")
    async def play_radio(
            self,
            ctx: discord.ApplicationContext,
            station: discord.Option(str, autocomplete=_get_station_list, description="Выберите станцию")):
        await ctx.defer()
        url = config.RADIO_LIST.get(station)
        if not url:
            await ctx.respond("Станция не найдена", ephemeral=True)
            return
        await self.play(ctx, url, station)


    @commands.slash_command(name="pause", description="Поставить на паузу или продолжить воспроизведение")
    async def pause_radio(self, ctx: discord.ApplicationContext):
        try:
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
        except Exception as e:
            err = f"Ошибка подключения: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="stop", description="Поставить на паузу или продолжить воспроизведение")
    async def stop_radio(self, ctx: discord.ApplicationContext):
        try:
            voice_client = ctx.guild.voice_client
            if not voice_client or (not voice_client.is_playing() and not voice_client.is_paused()):
                await ctx.respond("Сейчас ничего не воспроизводится", ephemeral=True)
                return

            if voice_client.is_playing():
                voice_client.stop()
                self.is_paused = True
                await ctx.respond("Остановлено")
        except Exception as e:
            err = f"Ошибка подключения: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="leave", description="Выйти из голосового канала")
    async def leave_radio(self, ctx: discord.ApplicationContext):
        try:
            if self.voice_client is None:
                await ctx.respond("Меня и так здесь нет", ephemeral=True)
                return
            await self.voice_client.disconnect()
            leave_msg = random.choice(config.LEAVE_RESPONSES)
            await ctx.respond(leave_msg)
            self.voice_client = None
        except Exception as e:
            err = f"Ошибка подключения: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="refresh", description="Обновить список радио")
    async def refresh_radio_list(self, ctx: discord.ApplicationContext):
        try:
            config.RADIO_LIST = load_radio_list()
            await ctx.respond("Список радиостанций обновлен")
        except Exception as e:
            err = f"Ошибка подключения: {e}"
            print(err)
            await ctx.respond(err)

def setup(bot):
    bot.add_cog(Radio(bot))
