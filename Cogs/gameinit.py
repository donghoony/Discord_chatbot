from discord.ext import commands
from Games.avalon import avalon
from Games.rsp import rsp

class GameInit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avl")
    async def avalon(self, ctx, *args):
        msg = "".join(args)
        if msg == "help":
            await avalon.avalon_help(ctx.channel)
        elif not msg:
            await avalon.avalon(self.bot, ctx.channel, ctx.author)

    @commands.command(name="rsp")
    async def rsp(self, ctx):
        await rsp.rsp_cycle(self.bot, ctx.channel, ctx.author)


def setup(bot):
    bot.add_cog(GameInit(bot))