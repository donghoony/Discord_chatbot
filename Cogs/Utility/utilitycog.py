from discord.ext import commands
import subprocess
from Cogs.Utility.UtilityFunctions import clearchat

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clr")
    async def clear(self, ctx):
        await clearchat.clear(ctx)

    @commands.command(name="stop")
    @commands.has_permissions(administrator=True)
    async def stop_bot(self, ctx):
        await ctx.message.delete()
        exit(0)

    @commands.command(name="update")
    @commands.has_permissions(administrator=True)
    async def update_bot(self, ctx):
        #only works on Linux
        await ctx.message.delete()
        subprocess.call(['sh', 'update.sh'])
        exit(0)


def setup(bot):
    bot.add_cog(UtilityCog(bot))
