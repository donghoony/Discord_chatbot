from discord.ext import commands
import asyncio
from collections import deque

from discord import FFmpegPCMAudio

from chatbot_secrets import KAKAO_KEY
from requests import post

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()
        self.KAKAO_KEY = KAKAO_KEY
        self.voices = ["WOMAN_READ_CALM", "MAN_READ_CALM", "WOMAN_DIALOG_BRIGHT", "MAN_DIALOG_BRIGHT"]
        self.current_voice = self.voices[3]
        self.audio_count = 0

    def cycle_audio(self):
        self.audio_count += 1
        if self.audio_count > 10:
            self.audio_count = 0

    def make_tts_kakao(self, speak_data):
        URL = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
        headers = {"Content-Type": "application/xml",
                   "Authorization": f"KakaoAK {self.KAKAO_KEY}"}
        data = f'<speak><voice name="{self.current_voice}"><prosody rate="slow">' +\
               speak_data.encode('utf-8').decode('latin1') + '</prosody></voice></speak>'
        res = post(URL, headers=headers, data=data)
        with open(f"tts_outputs/audio_{self.audio_count}.mp3", "wb") as f:
            f.write(res.content)
            f.close()
            return 1

    @commands.command(name="ts")
    async def tts_setting(self, ctx, *args):
        msg = "".join(args)
        if not msg:
            await ctx.channel.send("`!ts <번호>`로 목소리를 선택해주세요.\n\
                                    (1. 여성 낭독, 2. 남성 낭독, 3. 여성 대화, 4. 남성 대화)")
            return
        try:
            if 1 <= int(msg) <= 4:
                self.current_voice = self.voices[int(msg)-1]
        except:
            pass
        await ctx.channel.send("목소리가 변경되었습니다.")

    @commands.command(name="tts", aliases=['t'])
    async def tts_speech(self, ctx, *args):
        msg = " ".join(args)
        flag = self.make_tts_kakao(msg)
        if not flag:
            return
        voice_client = await self.join(ctx)

        file = FFmpegPCMAudio(f"tts_outputs/audio_{self.audio_count}.mp3")
        self.cycle_audio()

        async def queue_play_tts(file):
            self.queue.append(file)
            while 1:
                if not voice_client.is_playing():
                    voice_client.play(self.queue.popleft())
                    break
                else:
                    await asyncio.sleep(1)
        await queue_play_tts(file)


def setup(bot):
    bot.add_cog(TTSCog(bot))
