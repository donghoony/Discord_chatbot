from discord.ext import commands

class ErrorHandlerCog(commands.Cog):
    def __init__(self, bot):
        global botClient
        self.bot = bot
        botClient = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions):
            await ctx.message.delete()
            msg = await ctx.send(f"You are not strong enough, <@{ctx.message.author.id}>")
            await msg.delete(delay=3)

def setup(bot):
    bot.add_cog(ErrorHandlerCog(bot))
