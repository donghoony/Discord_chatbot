import asyncio
import discord
import random as r
from collections import deque

async def get_participants(game_name:str, client:discord.Client, channel:discord.TextChannel, author:discord.Member, min_player, max_player):
    msg = await channel.send(f"{game_name}에 참여하시려면 🔴를 눌러주세요.\n시작하시려면 주최자가 🆗을 눌러주세요.\n`제한시간 60초, 주최자 {author.nick}`")
    await msg.add_reaction("🔴")
    await msg.add_reaction("🆗")
    cached_msg = [x for x in client.cached_messages if x.id == msg.id][0]
    lack_message_new = lack_message_old = None

    def check(reaction, user):
        return str(reaction) == "🆗" and user == author        
        
    while 1:
        try:
            await client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            delayed = await channel.send("게임 모집 시간이 초과되었습니다. 진행을 취소합니다.")
            await msg.delete()
            await delayed.delete(delay=3)
            if lack_message_new is not None:
                await lack_message_new.delete()
            return None

        reacted_users = await cached_msg.reactions[0].users().flatten()
        participants = [x for x in reacted_users if not x.bot]
        
        if not min_player <= len(participants) <= max_player:
            lack_message_new = await channel.send(f"플레이어가 부족합니다. `{min_player} ~ {max_player}명`의 플레이어가 필요합니다. (현재 `{len(participants)}`명)")
            await cached_msg.reactions[1].remove(author)
            if lack_message_old is not None:
                await lack_message_old.delete()
            lack_message_old = lack_message_new
            await lack_message_old.delete(delay=3)
        else:
            break

    await msg.delete()
    start_msg = await channel.send(f"아래 {len(participants)}명이 게임에 참여합니다.\n`{', '.join([x.nick for x in participants])}`")
    await start_msg.delete(delay=5)
    participants = deque(participants)
    r.shuffle(participants)
    return participants
