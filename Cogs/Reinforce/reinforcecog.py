from discord.ext import commands
from Cogs.Reinforce.item import Item
import asyncio
from Cogs.Reinforce import pklinventory

class ReinforceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="rrank", aliases=["강화순위"])
    async def rankings(self, ctx):
        items = pklinventory.load()
        a = [items[x].__dict__ for x in items]
        a.sort(key=lambda x: -x['level'])
        text = ""
        cnt = 1
        for i in range(len(a)):
            cur = a[i]
            user = ctx.guild.get_member(cur['owner_id'])
            if user is None:
                continue
            text += f"{cnt}. {user.nick if user.nick else user.name} : " \
                    f"{cur['level']} ( {cur['maximum_level']}🔺, "\
                    f"{cur['reinforced_count']}🔨"
            if cur['broken_count']:
                text += f", {cur['broken_count']}💣)\n"
            else:
                text += " )\n"
            cnt += 1
        await ctx.channel.send(text)

    @commands.command(name="r", aliases=["강화"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reinforce(self, ctx, name):
        author = ctx.message.author
        user_name = author.nick if author.nick else author.name
        user_id = author.id
        await ctx.message.delete()
        items = pklinventory.load()
        try:
            item = items[user_id]
        except KeyError:
            item = items[user_id] = Item(user_id, name)
        result, odd, before, after = item._reinforce_item()

        res = ["💥실패💥", "✨성공✨", "💣파괴💣"][result]
        pklinventory.save_result(item)
        for i in range(len(after)):
            if i == 0:
                await ctx.channel.send(f"{user_name}: {name} **강화 {res}** {before} ➡️ {after[0]} (**{'-+- '[result]}{abs(after[i]-before)}**, {odd}%)")
            else:
                await ctx.channel.send(f"{user_name}: {name} **✨강화 연속 성공✨** {after[i-1]} ➡️ {after[i]} (**{'-+- '[result]}{abs(after[i]-after[i-1])}**)")
            await asyncio.sleep(1)

    @reinforce.error
    async def cooldown(self, ctx, error):
        author = ctx.message.author
        name = author.nick if author.nick else author.name
        await ctx.message.delete()
        msg = await ctx.channel.send(f"{name}_ 다음 강화까지 남은 시간: {error.retry_after:1.0f}초.")
        await msg.delete(delay=error.retry_after)

def setup(bot):
    bot.add_cog(ReinforceCog(bot))