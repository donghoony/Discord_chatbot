import discord
import asyncio
from Models import game

async def rsp_dm(member:discord.Member, is_draw:bool):
    channel = await member.create_dm()
    message = await channel.send(("비겼습니다. " if is_draw else "") + "`가위`, `바위`, `보` 중 하나를 선택해주세요. 선택 후 메시지가 사라지지 않는다면 다시 선택해 주세요.")
    await message.add_reaction("\u270A")
    await message.add_reaction("\u270C")
    await message.add_reaction("\u270B")
    return message

async def result_dm(member, message):
    channel = await member.create_dm()
    embed = discord.Embed(title="결과", url=message.jump_url, color=666111)
    embed.set_footer(icon_url=message.channel.guild.icon_url, text=message.channel.guild.name)
    await channel.send(embed=embed)

async def rsp_get_hand(client:discord.Client, player:discord.Member, message:discord.Message):
    rsp_list = ["\u270A", "\u270C", "\u270B"]
    def check(reaction, user):
        return reaction.emoji in rsp_list and user == player
    reaction, user = await client.wait_for("reaction_add", check=check)
    reaction_idx = rsp_list.index(reaction.emoji)
    await message.delete()
    await message.channel.send(f"{['바위', '가위', '보'][reaction_idx]}를 선택하셨습니다.")
    return [reaction_idx, user]

async def rsp_judge(hand_1, hand_2):
    p1_hand, p2_hand = hand_1[0], hand_2[0]
    #주먹가위보 -> 012
    if p1_hand == p2_hand:
        return None
    elif (p1_hand, p2_hand) in ((0, 1), (1, 2), (2, 0)):
        return hand_1, hand_2
    else:
        return hand_2, hand_1

async def rsp(client:discord.Client, channel, author):
    rsp_list = ["\u270A", "\u270C", "\u270B"]
    participants = await game.get_participants("가위바위보", client, channel, author, 2, 2)
    player1, player2 = list(participants)
    await channel.send("게임을 시작합니다. 개인 메시지를 확인해 주세요.")

    is_draw = False
    while 1:
        t1 = asyncio.create_task(rsp_dm(player1, is_draw))
        t2 = asyncio.create_task(rsp_dm(player2, is_draw))

        player1_info_message = await t1
        player2_info_message = await t2
        #except:
        #    await channel.send("개인 메시지를 보낼 수 없어 게임을 종료합니다.")
        #    return

        t3 = asyncio.create_task(rsp_get_hand(client, player1, player1_info_message))
        t4 = asyncio.create_task(rsp_get_hand(client, player2, player2_info_message))

        hand_1 = await t3
        hand_2 = await t4

        result = await rsp_judge(hand_1, hand_2)
        if result == None:
            is_draw = True
            continue
        winner, loser = result
        winner_hand, winner_id = winner[0], winner[1].id
        loser_hand, loser_id = loser[0], loser[1].id
        break

    embed = discord.Embed(
        title="가위바위보 결과",
        colour=discord.Colour.purple()
    )
    embed.add_field(name="     승자", value=f"{rsp_list[winner_hand]}<@{winner_id}>", inline=True)
    embed.add_field(name="     패자", value=f"{rsp_list[loser_hand]}<@{loser_id}>", inline=True)
    await channel.send(embed=embed)
    result_message = await channel.send(f"<@{winner_id}> 승!")

    r1 = asyncio.create_task(result_dm(player1,result_message))
    r2 = asyncio.create_task(result_dm(player2,result_message))
    await r1; await r2

    return winner[1].id, loser[1].id

async def rsp_cycle(client, channel, author):
    winner, loser = await rsp(client, channel, author)
