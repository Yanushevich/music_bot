import discord
from discord.ext import commands
import config
import random
import aiohttp
import asyncio
import csv


def load_radio_list():
    station_list = []
    with open('cogs/stations.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            station_list.append(row)
    return station_list


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_audio_url = None
        self.current_data_url = None
        self.voice_client = None
        self.is_paused = False
        self.track_task = None
        self.message = None

    async def _get_station_list(ctx: discord.AutocompleteContext):
        try:
            query = str(ctx.options['station']).strip().lower()
            results = {}
            for station in config.RADIO_LIST:
                name = station['station']
                if query in name.lower():
                    results[name] = station['audio_url']
                    if len(results) >= 25:
                        break
            return results
        except Exception as e:
            print(f"Ошибка в автозаполнении: {e}")
            return []

    async def _disconnect_all(self, guild: discord.Guild):
        for vc in self.bot.voice_clients:
            if vc.guild == guild:
                print(f"Отключаю голосовое соединение в гильдии {guild.id}")
                await vc.disconnect()
        print("Очистка соединений завершена")

    async def _connect(self, ctx: discord.ApplicationContext):
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

    async def _fetch_current_track(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.current_data_url) as resp:
                data = await resp.json()
                track = data['result']['history'][0]
                return f" ({track['artist']} - {track['song']})"

    async def _update_track_info(self, ctx: discord.ApplicationContext):
        try:
            while True:
                new_track_info = await self._fetch_current_track()
                if self.message is not None:
                    await self.message.edit(content=self.message.content + new_track_info)
                await asyncio.sleep(15)
        except Exception as e:
            err = f"Ошибка получения информации о треке: {e}"
            print(err)
            await ctx.respond(err)
            return None

    async def play(self, ctx: discord.ApplicationContext, station):
        try:
            for s in config.RADIO_LIST:
                if s['station'] == station:
                    self.current_audio_url = s.get('audio_url')
                    self.current_data_url = s.get('data_url')
                    break
            if not ctx.guild.voice_client:
                self.voice_client = await self._connect(ctx)
                if self.voice_client is None:
                    await ctx.respond("Не удалось подключиться к голосовому каналу.")
                    return
            else:
                self.voice_client = ctx.guild.voice_client
                if self.voice_client.is_playing():
                    self.voice_client.stop()
            source = discord.FFmpegPCMAudio(self.current_audio_url, **config.FFMPEG_OPTIONS)
            self.voice_client.play(source)
            if self.track_task and not self.track_task.done():
                self.track_task.cancel()
            play_msg = random.choice(config.PLAY_RESPONSES) + station
            self.message = await ctx.respond(play_msg)
            self.track_task = asyncio.create_task(self._update_track_info(ctx))
        except Exception as e:
            err = f"Ошибка воспроизведения: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="play", description="Воспроизвести радиостанцию")
    async def play_radio(
            self,
            ctx: discord.ApplicationContext,
            station: discord.Option(str, autocomplete=_get_station_list, description="Выберите станцию")):
        await ctx.defer()
        if not station:
            await ctx.respond("Станция не найдена", ephemeral=True)
            return
        await self.play(ctx, station)


    @commands.slash_command(name="pause", description="Поставить на паузу или продолжить воспроизведение")
    async def pause_radio(self, ctx: discord.ApplicationContext):
        try:
            if not self.voice_client or (not self.voice_client.is_playing() and not self.voice_client.is_paused()):
                await ctx.respond("Сейчас ничего не воспроизводится", ephemeral=True)
                return

            if self.voice_client.is_playing():
                self.voice_client.pause()
                self.is_paused = True
                if self.track_task is None or self.track_task.done():
                    self.track_task = asyncio.create_task(self._update_track_info(ctx))
                self.is_paused = False
                await ctx.respond("Пауза")
            elif self.voice_client.is_paused():
                self.voice_client.resume()
                self.is_paused = False
                await ctx.respond("Продолжаем")
                if self.track_task and not self.track_task.done():
                    self.track_task.cancel()
                self.is_paused = True
        except Exception as e:
            err = f"Ошибка паузы: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="stop", description="Поставить на паузу или продолжить воспроизведение")
    async def stop_radio(self, ctx: discord.ApplicationContext):
        try:
            if not self.voice_client or (not self.voice_client.is_playing() and not self.voice_client.is_paused()):
                await ctx.respond("Сейчас ничего не воспроизводится", ephemeral=True)
                return

            if self.voice_client.is_playing():
                self.voice_client.stop()
                self.is_paused = True
                await ctx.respond("Остановлено")
            if self.track_task and not self.track_task.done():
                self.track_task.cancel()
                self.track_task = None
        except Exception as e:
            err = f"Ошибка остановки: {e}"
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
            err = f"Ошибка выхода: {e}"
            print(err)
            await ctx.respond(err)

    @commands.slash_command(name="refresh", description="Обновить список радио")
    async def refresh_radio_list(self, ctx: discord.ApplicationContext):
        try:
            config.RADIO_LIST = load_radio_list()
            await ctx.respond("Список радиостанций обновлен")
        except Exception as e:
            err = f"Ошибка обновления списка станций: {e}"
            print(err)
            await ctx.respond(err)

def setup(bot):
    bot.add_cog(Radio(bot))
