"""
!g+ <game_role_name>: Makes new role
!g- <game_role_name>: Deletes role

그냥 채널 하나에 메시지들 띄우고 Reaction으로 관리하면??
"""

# 역할 채널: 876358702335152148

import discord
from discord.ext import commands
from typing import Union

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.role_channel_id = 876358702335152148
        self.bot = bot

    def _check(self, channel_id) -> bool:
        return self.role_channel_id == channel_id

    def _get_name_from_content(self, ctx) -> str:
        text = ctx.message.content
        role_name = text.split()[1]
        return role_name

    def _get_role_by_name(self, guild:discord.Guild, role_name) -> Union[discord.Role, None]:
        guild_role_list = guild.roles
        for role in guild_role_list:
            if role.name == "+" + role_name:
                return role
        return None

    async def _delete_role_message(self, channel, role_name):
        role_message = None
        history = await channel.history(limit=None).flatten()
        for m in history:
            if m.content == role_name:
                role_message = m
                break
        if role_message is None:
            return
        await role_message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if self._check(payload.channel_id):
            await self.get_payload(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if self._check(payload.channel_id):
            await self.get_payload(self.bot, payload)

    @commands.command(name="g+")
    @commands.has_permissions(administrator=True)
    async def create_role(self, ctx):
        # !g+ <role_name> | !g- <role_name>
        role_name = self._get_name_from_content(ctx)
        await self._create_role(ctx.guild, role_name)
        await ctx.message.delete()
        role_message = await ctx.send(role_name)
        await role_message.add_reaction("\U0001F534")

    @commands.command(name="g-")
    @commands.has_permissions(administrator=True)
    async def delete_role(self, ctx):
        role_name = self._get_name_from_content(ctx)
        await self._delete_role(ctx.guild, role_name)
        await ctx.message.delete()
        await self._delete_role_message(ctx.channel, role_name)

    @commands.command(name="setchannel_role")
    @commands.has_permissions(administrator=True)
    async def _set_role_channel(self, ctx):
        self.role_channel_id = ctx.channel.id
        await ctx.send("OK!")

    async def _delete_role(self, guild, role_name):
        role = self._get_role_by_name(guild, role_name)
        if role:
            await role.delete(reason="Removed by Bot command")

    async def _create_role(self, guild:discord.Guild, role_name):
        role = self._get_role_by_name(guild, role_name)
        if role:
            return
        await guild.create_role(name="+"+role_name, reason="Created by Bot command", mentionable=True, colour=discord.Colour.random())

    async def role_reaction(self, message, user:discord.Member, event_type):
        role = self._get_role_by_name(user.guild, message.content)
        if event_type == "REACTION_ADD":
            await user.add_roles(role)
        else:
            await user.remove_roles(role)

    async def get_payload(self, bot, payload):
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        user_id = payload.user_id
        message_id = payload.message_id
        event_type = payload.event_type

        guild = bot.get_guild(guild_id)
        channel = bot.get_channel(channel_id)
        user = guild.get_member(user_id)
        message = discord.utils.get(await channel.history(limit=None).flatten(), id=message_id)

        await self.role_reaction(message, user, event_type)

def setup(bot):
    bot.add_cog(RoleCog(bot))



