import asyncio
import discord
from discord.ext import commands
import youtube_dl
import re
import requests
import html
from collections import deque
from chatbot_secrets import YOUTUBE_KEY

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.yturlpattern = r'(https?:\/\/)?(youtu.be\/|youtube.com\/|www.youtube.com\/).*'
        self.YDL_OPTIONS = {'format':'bestaudio','noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.YOUTUBE_KEY = YOUTUBE_KEY
        self.queue = deque()

    async def play_url(self, ctx, url):
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(URL, **self.FFMPEG_OPTIONS), volume=0.02)
        voice_client = await self.get_current_voice_client()
        if not voice_client:
            voice_client = await self.join(ctx)
        voice_client.play(source)

    @commands.command(name="volume", aliases=['v'])
    async def set_volume(self, ctx, value):
        pass

    @commands.command(name="play", aliases=['p'])
    async def search_play(self, ctx, *arg):
        arg = " ".join(arg)
        await ctx.message.delete()
        if re.match(self.yturlpattern, arg):
            url = arg
        else:
            url = await self.search(ctx, arg)

        if url:
            await self.play_url(ctx, url)

    async def search(self, ctx, arg):
        r = requests.get(f"https://www.googleapis.com/youtube/v3/search?key={self.YOUTUBE_KEY}&maxResults=10&type=video&part=snippet&q="+arg)
        inner_text = ""
        video_ids = []
        for cnt, x in enumerate(r.json()['items'], start=1):
            # too slow to implement
            #video_id = x['id']['videoId']
            #rr = requests.get(f"https://www.googleapis.com/youtube/v3/videos?key={self.YOUTUBE_KEY}&part=contentDetails&id="+video_id)
            #duration = rr.json()['items'][0]['contentDetails']['duration']
            #print(x['snippet']['title'], end=" ")
            #m, s = map(int, duration[2:-1].split("M"))
            #print(f"{m}:{s:02d}")
            inner_text += f"**{cnt:2d})** {html.unescape(x['snippet']['title'])}\n"
            video_ids.append(x['id']['videoId'])
        embed = discord.Embed()
        embed.add_field(name="Page 1", value=inner_text)
        msg = await ctx.channel.send(embed=embed)

        def check(m):
            return re.match('^([1-9]|10)$', m.content) and m.author == ctx.message.author
        await msg.add_reaction("⬅️")
        await msg.add_reaction("➡️")
        try:
            picked_video_number_msg = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            await picked_video_number_msg.delete()

        picked_video_number = int(picked_video_number_msg.content)
        await msg.delete()
        await picked_video_number_msg.delete()
        return video_ids[picked_video_number-1]


def setup(bot):
    bot.add_cog(MusicCog(bot))
