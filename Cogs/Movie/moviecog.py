import requests
from bs4 import BeautifulSoup
from datetime import timedelta, datetime
from discord import Embed
from discord.ext import commands, tasks
from Cogs.Movie.screentime import ScreenTime
from discord import Colour
from json.decoder import JSONDecoder
import xml.etree.ElementTree as ET

class MovieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.beforemsg = None
        self.no_IMAX_date = "20211226"
        self.already_opened_set = set()
        self.printed_count = 1
        self.movie_remainseat_dict = dict()

    def IMAX_print_process(self):
        print(".", end="" if self.printed_count%100 else "\n")
        self.printed_count += 1

    async def find_IMAX(self, ctx):
        while 1:
            self.IMAX_print_process()
            table = self.search_movie(self.no_IMAX_date)
            if not table:
                return
            imax = any([i.IMAX for i in table])
            if imax:
                await ctx.send(f"IMAX OPEN {self.no_IMAX_date}", embed=self.get_embed([x for x in table if x.IMAX]))
                self.no_IMAX_date = str(datetime.strptime(self.no_IMAX_date, "%Y%m%d") + timedelta(days=1)).replace("-", "", -1)[:8]
            else:
                break

    def search_movie(self, date):
        url = "http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?areacode=01&theatercode=0013&date="
        final_url = url + date
        res = requests.get(final_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        selected_date = soup.find("a", attrs={"title": "현재 선택"})
        start_idx = selected_date['href'].find("date=")
        selected_date = selected_date['href'][start_idx+5:start_idx+13]
        if date != selected_date:
            return []
        ls = soup.find_all("div", attrs={'class':'info-timetable'})
        timetable = []
        for i in ls:
            t = i.find_all("a")
            if not t:
                continue
            if "20027596" in t[0]['href']:
                timetable += [ScreenTime(x, date=date) for x in t]
        return timetable

    def search_movie_deeper(self, date):
        url = "http://ticket.cgv.co.kr/CGV2011/RIA/CJ000.aspx/CJ_HP_TIME_TABLE"
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4692.56 Safari/537.36",
                   "Accept":"application/json, text/javascript, */*; q=0.01",
                   "Content-Type":"application/json",
                   "X-Requested-With":"XMLHttpRequest"}
        json_body = {"REQSITE":"x02PG4EcdFrHKluSEQQh4A==","MovieGroupCd":"4h5e0F6BOQ8nzPmVqjuy+g==","TheaterCd":"LMP+XuzWskJLFG41YQ7HGA==",
                     "PlayYMD":"QuBGrFzyucrUVVyggOh6Ig==","MovieType_Cd":"nG6tVgEQPGU2GvOIdnwTjg==","Subtitle_CD":"nG6tVgEQPGU2GvOIdnwTjg==",
                     "SOUNDX_YN":"nG6tVgEQPGU2GvOIdnwTjg==","Third_Attr_CD":"nG6tVgEQPGU2GvOIdnwTjg==","IS_NORMAL":"nG6tVgEQPGU2GvOIdnwTjg==","Language":"zqWM417GS6dxQ7CIf65+iA=="}
        decoder = JSONDecoder()
        response = requests.post(url, headers=headers, json=json_body)
        content = response.content.decode('utf-8')
        content = decoder.decode(content)['d']['data']['DATA']
        root = ET.fromstring(content)
        ret = []
        for item in root:
            s = ScreenTime(tag=None)
            s.init_with_element(item)
            ret += [s]
        return ret

    def get_new_opened_screen(self, table):
            ret = []
            for movie in table:
                if movie.screen not in self.already_opened_set:
                    self.already_opened_set.add(movie.screen)
                    ret.append(movie.screen)
            return ret

    def get_embed(self, table):
        embed = Embed(title=f"UPDATE: {str(datetime.now())[:-7]}", colour=Colour.orange())
        before_movie = ScreenTime(None)
        for i in table:
            i:ScreenTime
            if i.screen != before_movie.screen:
                embed.add_field(inline=False, name="- "*30, value=f"**{i.screen}**")
            embed.add_field(name=f"{i.startTime} ~ {i.endTime}",
                            value=f"잔여 {i.remainSeats}석 ([LINK]({i.url}))" if i.remainSeats > 0 else "~~매진~~",
                            inline=True)
            before_movie = i
        return embed

    def check_lost_ticket(self, screen:ScreenTime):
        try:
            if self.movie_remainseat_dict[screen.tuplize()] != screen.remainSeats:
                return screen
        except KeyError:
            return None
        return None

    @tasks.loop(seconds=5)
    async def run(self, ctx):
        await self.find_IMAX(ctx)
        table = self.search_movie_deeper("20211225")
        for screen in self.get_new_opened_screen(table):
            await ctx.send(f"{screen} OPENED")

        # 취소표 발견시 알림
        for screen in table:
            screen : ScreenTime
            if self.check_lost_ticket(screen) is not None:
                await ctx.send(embed=Embed().add_field(name=f"**{screen.screen} ({screen.startTime} ~ {screen.endTime})**",
                                                       value=f"취소표 발생: [LINK]({screen.url or ''})"))
            self.movie_remainseat_dict[screen.tuplize()] = screen.remainSeats

        try:
            await self.beforemsg.edit(embed=self.get_embed(table))
        except:
            self.beforemsg = await ctx.send(embed=self.get_embed(table))

    @commands.command("movie")
    async def movie(self, ctx):
        channel = ctx.channel
        await ctx.message.delete()
        if not self.run.is_running():
            await ctx.send("Searching CGV - IMAX / SPIDERMAN NO WAY HOME")
            await self.run.start(channel)
        else:
            self.run.cancel()
            msg = await ctx.send("Stopped.")
            if self.beforemsg:
                await self.beforemsg.delete()
                self.beforemsg = None
            await msg.delete(delay=3)

def setup(bot):
    bot.add_cog(MovieCog(bot))
