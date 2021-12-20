from discord.ext import commands
from time import time
from discord import FFmpegPCMAudio
import asyncio

from Cogs.VoiceClient.texttospeech import TTSCog
from Cogs.music import MusicCog

class VoiceClientCog(TTSCog, MusicCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.latest_play = ["CHANNEL_ID", time()]
        self.bot = None

    async def get_current_voice_client(self):
        if len(self.bot.voice_clients) > 0:
            return self.bot.voice_clients[0]
        else:
            return None

    @commands.command(name="join", aliases=['j'])
    async def join(self, ctx):
        voice_client = await self.get_current_voice_client()
        if voice_client:
            return voice_client
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        return voice_client

    @commands.command(name="leave", aliases=['l'])
    async def leave(self, ctx):
        voice_client = await self.get_current_voice_client()
        if voice_client:
            bye = FFmpegPCMAudio("Cogs/VoiceClient/farewell.mp3")
            voice_client.play(bye)
            await asyncio.sleep(2.5)
            await voice_client.disconnect()

def setup(bot):
    bot.add_cog(VoiceClientCog(bot))
