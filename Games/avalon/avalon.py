import discord
import asyncio
from Games.avalon.avalon_character import *
from collections import deque
import random as r
import re
from Models import game


async def avalon_set_role(participants, setup_code):
    good_characters = {"merlin": Merlin(),
                       "percival": Percival(),
                       "servant_1": ArthursServants(0),
                       "servant_2": ArthursServants(1),
                       "servant_3": ArthursServants(2),
                       "servant_4": ArthursServants(3),
                       "servant_5": ArthursServants(4)
                       }
    evil_characters = {"assassin": Assassin(),
                       "mordred": Mordred(),
                       "morgana": Morgana(),
                       "oberon": Oberon(),
                       "minion_1": MinionsOfMordred(0),
                       "minion_2": MinionsOfMordred(1),
                       "minion_3": MinionsOfMordred(2)
                       }

async def avalon_setup_characters(participants, setup_code):
    # Players: 5 6 7 8 9 10
    # Goods  : 3 4 4 5 6 6
    # Evils  : 2 2 3 3 3 4
    # setup_code
    # 1: normal, only merlin, assassin
    # 2: added some, merlin, assassin, morgana, percival
    # 3: added some, merlin, assassin, mordred, percival
    # 4: added all, merlin, assassin, morgana, percival, oberon,

    players_count = len(participants)
    r.shuffle(participants)

    good_count = [0, 1, 1, 1, 2, 3, 4, 4, 5, 6, 6]
    evil_count = [0, 0, 1, 2, 2, 2, 2, 3, 3, 3, 4]

    good_players = []
    evil_players = []
    minion_count = servant_count = 0

    for i in range(good_count[players_count]):
        current_player = participants.popleft()
        if i == 0:
            good_players.append([current_player, Merlin()])
            print("Added Merlin")
        elif setup_code == 2 and i == 1:
            good_players.append([current_player, Percival()])
            print("Added Percival")
        else:
            good_players.append([current_player, ArthursServants(servant_count)])
            servant_count += 1
            print("Added Servant")

    for i in range(evil_count[players_count]):
        current_player = participants.popleft()
        if i == 0:
            evil_players.append([current_player, Assassin()])
            print("Added Assassin")
        elif setup_code in (2, 4) and i == 1:
            evil_players.append([current_player, Morgana()])
            print("Added Morgana")
        elif setup_code in (3, 4) and i == 1:
            evil_players.append([current_player, Mordred()])
            print("Added Mordred")
        elif setup_code == 4 and i == 2:
            evil_players.append([current_player, Oberon()])
            print("Added Oberon")
        else:
            evil_players.append([current_player, MinionsOfMordred(minion_count)])
            minion_count += 1
            print("Added Minion")
    return good_players, evil_players

# announce type_cards by dm message
async def avalon_setup_announce(global_channel:discord.TextChannel, good_players:list, evil_players:list):
    for i in good_players:
        channel = await i[0].create_dm()
        embed = discord.Embed(
            title = i[1].name_kr,
            description = i[1].description,
            colour = discord.Colour.blue()
        )
        embed.set_thumbnail(url=i[1].url)
        embed.add_field(name="선악 여부", value='선')
        if type(i[1]) == Percival:
            merlins = [i[0].nick for i in good_players if type(i[1]) == Merlin] + [i[0].nick for i in evil_players if type(i[1]) == Morgana]
            r.shuffle(merlins)
            embed.add_field(name="멀린", value=", ".join(merlins))

        if type(i[1]) == Merlin:
            bad_boys = [i[0].nick for i in evil_players if type(i[1]) != Mordred]
            embed.add_field(name="악의 정체", value=", ".join(bad_boys) if bad_boys else "-")

        await channel.send("당신의 역할 카드입니다.", embed=embed)

    visible_evil_names = [i[0].nick for i in evil_players if type(i[1]) != Oberon]
    for i in evil_players:
        channel = await i[0].create_dm()
        embed = discord.Embed(
            title=i[1].name_kr,
            description=i[1].description,
            colour=discord.Colour.red()
        )
        embed.set_thumbnail(url=i[1].url)
        embed.add_field(name="선악 여부", value='악')
        visible_evil_names.remove(i[0].nick)
        embed.add_field(name="다른 악 플레이어", value = ", ".join(visible_evil_names) if visible_evil_names else '-')
        visible_evil_names.append(i[0].nick)
        await channel.send("당신의 역할 카드입니다.", embed=embed)

    message = await global_channel.send("역할 카드를 나눠드렸습니다. 3초 후 게임을 시작합니다.")
    await global_channel.send(f"**선 {len(good_players)}명, 악 {len(evil_players)}명**")
    await asyncio.sleep(1)
    for i in range(2, -1, -1):
        await message.edit(content=f"역할 카드를 나눠드렸습니다. {i}초 후 게임을 시작합니다.")
        if i == 0:
            break
        await asyncio.sleep(1)
    await message.edit(content="게임을 시작합니다.")

async def avalon_setup_turn_announce(channel:discord.TextChannel, participants:deque, shuffle_state):
    if shuffle_state:
        r.shuffle(participants)
    else:
        msg = " -> ".join([x[0].nick for x in participants]) + " -> " + participants[0][0].nick
        await channel.send("게임 진행 순서는 다음과 같습니다.\n```" + msg + "```")

async def avalon_setup(channel:discord.TextChannel, participants:deque, setup_code):
    """ DO NOT THROW PARTICIPANTS FOR ARGUMENTS BY RAW """
    good_players, evil_players = await avalon_setup_characters(deque([x for x in participants]), setup_code)
    await avalon_setup_announce(channel, good_players, evil_players)
    participants = deque([x for x in good_players] + [y for y in evil_players])
    # print(*[(x[0].nick, type(x[1])) for x in participants], sep='\n')
    await avalon_setup_turn_announce(channel, participants, True)
    return deque(participants)

"RETURNS QUEST_MEMBER WHICH IS A LIST OF STRING"
async def avalon_build_quest_team(client:discord.Client, channel:discord.TextChannel, players:deque, quest_num):
    leader = players[0]
    quest_member = []
    players_id = [str(x[0].id) for x in players]
    quest_limit = [[0, 0, 0, 0, 0],
                 [1, 1, 1, 1, 1],
                 [2, 2, 2, 2, 2],
                 [2, 2, 2, 2, 2],
                 [2, 2, 2, 2, 2],
                 [2, 3, 2, 3, 3],
                 [2, 3, 4, 3, 4],
                 [2, 3, 3, 4, 4],
                 [3, 4, 4, 5, 5],
                 [3, 4, 4, 5, 5],
                 [3, 4, 4, 5, 5]]
    cur_quest_limit = quest_limit[len(players)][quest_num]

    embed = discord.Embed(
        title="원정대 후보",
        description=f"필요한 원정대 인원 : {cur_quest_limit}명",
        colour=discord.Colour.dark_gold()
    )
    for i in range(len(players)):
        embed.add_field(name=players[i][0].nick, value=str(i+1), inline=False if i == 5 else True)

    await channel.send(f"현재 대표는 <@{leader[0].id}> 입니다. 원정대 {cur_quest_limit}명을 꾸려 주세요.", embed=embed)
    await channel.send("원정대를 선정할 때는 `!원정대 1 2`와 같이 입력합니다.")

    def check(message):
        if message.author.id == leader[0].id and (message.content.startswith("!출발") or message.content.startswith("!원정대")) and message.channel == channel:
            return True
        return False

    while 1:

        valid = True
        message = await client.wait_for("message", check=check)
        message_content = message.content
        await message.delete()
        if message_content.startswith("!원정대"):
            quest_member = []
            if len(message_content.split(" "))-1 != cur_quest_limit:
                await channel.send(f"입력하신 원정대 구성원 수`({len(message_content.split(' '))-1})`와 현재 구성해야하는 원정대 구성원 수`({cur_quest_limit})`가 맞지 않습니다.")
                continue
            user_input_possibility = [str(x) for x in range(1, len(players)+1)]
            for user_number_in_str in message_content.split(" ")[1:]:
                if user_number_in_str not in user_input_possibility:
                    await channel.send(f"입력하신 문자 `({user_number_in_str})`가 후보 번호에 있지 않습니다. 정확히 입력해주세요. ex)`!원정대 1 2`")
                    valid = False
                    break
                quest_member.append(str(players[int(user_number_in_str)-1][0].id))
            if not valid:
                continue

            embed = discord.Embed(
                title=f"원정대 구성원 ({quest_num+1}차 원정)",
                colour=discord.Colour.dark_gold()
            )
            for i in range(len(quest_member)):
                embed.add_field(name=f"원정대 {i+1}", value=f"<@{quest_member[i]}>")

            await channel.send(f"원정대를 꾸렸습니다. 표결을 진행하려면 `!출발`을 입력해주세요.", embed=embed)
            continue
        if message_content.startswith("!출발"):

            if len(quest_member) != cur_quest_limit:
                await channel.send(f"원정에 떠나기 위한 구성원의 수`({cur_quest_limit})`와 현재 구성원의 수`({len(quest_member)})`가 다릅니다.")
                continue
            else:
                break
    players.rotate(-1)
    return quest_member

async def avalon_vote_quest_team(client:discord.Client, channel:discord.channel, quest_team:list, players:deque, vote_fail_cnt):
    message = await channel.send("원정대 구성에 관한 투표를 진행합니다.")
    if vote_fail_cnt:
        await channel.send(f"현재 투표가 총 `{vote_fail_cnt}회` 거부되었습니다. `5회` 투표가 거부되면 즉시 악이 승리합니다.")
    await asyncio.sleep(2)
    vote_yes, vote_no = await avalon_vote(client, [x for x in players], True)
    r.shuffle(vote_yes)
    r.shuffle(vote_no)
    vote_success = len(vote_yes) > len(vote_no)

    embed = discord.Embed(
        title="투표 결과",
        description="구성안이 통과되었습니다." if vote_success else "구성안이 거부되었습니다.",
        colour=discord.Colour.blue() if vote_success else discord.Colour.red()
    )
    embed.add_field(name="찬성", value=", ".join(["<@"+ str(x) +">" for x in vote_yes]) if vote_yes else "-")
    embed.add_field(name="반대", value=", ".join(["<@"+ str(x) +">" for x in vote_no]) if vote_no else "-", inline=False)
    await channel.send("투표 결과입니다.", embed=embed)
    if vote_success:
        return True
    else:
        return False

async def avalon_vote(client:discord.Client, voters:list, is_quest_team_vote:bool):
    "voters contains Members"
    UP_EMOJI = "\U0001F44D" if is_quest_team_vote else "\u2B55"
    DOWN_EMOJI = "\U0001F44E" if is_quest_team_vote else "\u274C"
    msgs = []
    channels = []
    max_voters = len(voters)
    up = []
    down = []
    users_id = []

    r.shuffle(voters)
    for i in voters:
        channel = await i[0].create_dm()
        channels.append(channel)
        users_id.append(channel.recipient.id)
        message = await channel.send(("원정대 구성에 관한 " if is_quest_team_vote else "원정 결과에 대한 ") + "투표를 진행합니다.\n투표 이후 메시지가 사라지지 않으면 다시 투표해 주세요." + ("\n**선은 원정 결과에 대한 투표에 성공표만 낼 수 있습니다.**" if not is_quest_team_vote and i[1].side == GOOD else ""))
        await message.add_reaction(UP_EMOJI)
        if is_quest_team_vote or (not is_quest_team_vote and i[1].side == EVIL):
            await message.add_reaction(DOWN_EMOJI)
        msgs.append(message)

    def check(reaction, user):
        if reaction.emoji in [UP_EMOJI, DOWN_EMOJI] and reaction.message.channel in channels and user.id in users_id:
            channels.remove(reaction.message.channel)
            return True
        return False

    for i in range(max_voters):
        reaction, user = await client.wait_for("reaction_add", check=check)
        message = msgs[users_id.index(user.id)]
        await message.delete()
        if reaction.emoji == UP_EMOJI:
            up.append(user.id)
            vote_message = await message.channel.send("투표에 찬성하셨습니다." if is_quest_team_vote else "원정 성공에 투표하셨습니다.")
        if reaction.emoji == DOWN_EMOJI:
            down.append(user.id)
            vote_message = await message.channel.send("투표에 반대하셨습니다." if is_quest_team_vote else "원정 실패에 투표하셨습니다.")
        await asyncio.sleep(1.5)
        await vote_message.delete()
    return (up, down)

async def avalon_quest(client:discord.Client, channel:discord.TextChannel, quest_team:list, players:deque, round_number):
    await channel.send("원정대에 한해, 원정 성공 여부 투표를 진행합니다.")
    r.shuffle(players)
    special_round = len(players) >= 7 and round_number == 3
    if special_round:
        await channel.send("이번 라운드는 실패가 2표 이상이어야 원정에 실패합니다.")
    quest_team_members = [x for x in players if str(x[0].id) in quest_team]
    vote_yes, vote_no = await avalon_vote(client, quest_team_members, False)
    vote_yes, vote_no = len(vote_yes), len(vote_no)
    vote_success = (vote_no < 2) if special_round else (not vote_no)
    embed = discord.Embed(
        title="원정 결과",
        description="원정 진행을 성공하였습니다." if vote_success else "원정 진행을 실패했습니다.",
        colour=discord.Colour.blue() if vote_success else discord.Colour.red()
    )
    embed.add_field(name="원정 성공 표", value=str(vote_yes))
    embed.add_field(name="원정 실패 표", value=str(vote_no))
    await channel.send(f"원정대가 다녀왔습니다.\n`{', '.join(x[0].nick for x in players if str(x[0].id) in quest_team)}`")
    await channel.send("원정 결과입니다.", embed=embed)

    msg = await channel.send("7초 후 다음 라운드를 진행합니다.")
    for i in range(7, -1, -1):
        await msg.edit(content=f"{i}초 후 다음 라운드를 진행합니다.")
        await asyncio.sleep(1)

    if vote_success:
        return True
    else:
        return False

async def avalon_board_embed(total_quest_stat):
    embed = discord.Embed(
        title="아발론: 원정 현황",
        description="",
        colour=discord.Colour.green()
    )
    embed.set_footer(text="원정을 세 번 실패하면 악의 승리입니다.")
    for i in range(5):
        embed.add_field(name=f"원정 {i+1}", value="\u2B55" if total_quest_stat[i] == 1 else "\u274C" if total_quest_stat[i] == 0 else "\u2753")
    embed.add_field(name="-", value='-')
    return embed

async def avalon_assassinate(client:discord.Client, channel:discord.TextChannel, players:deque):
    await channel.send("무사히 3번의 여정을 끝마쳤습니다.")
    assassin = [x[0] for x in players if type(x[1]) == Assassin][0]
    await channel.send(f"암살자의 암살 계획이 남아 있습니다.\n멀린으로 의심되는 사람을 상의 후 지목해 주세요.\n`!암살 (@플레이어)`")
    user_id = [str(x[0].id) for x in players]

    def check(message):
        return message.author == assassin and message.content.startswith("!암살") and len(message.content.split(" ")) == 2
    while 1:
        message = await client.wait_for("message", check=check)
        target_id = [x for x in re.findall("[0-9]*", message.content.split(" ")[1]) if x != ""]
        print(target_id)
        if target_id == []:
            await channel.send("정확한 플레이어를 지목해주세요. `!암살 (@플레이어)`")
            continue
        else:
            target_id = target_id[0]
            if target_id not in user_id:
                await channel.send("해당 플레이어는 게임에 속해있지 않습니다.")
                continue
            break

    target = [x[0] for x in players if type(x[1]) == Merlin][0]
    return str(target.id) == target_id

async def avalon_end(channel:discord.TextChannel, players:deque, win_side):
    evil_players = [x for x in players if x[1].side == EVIL]
    good_players = [x for x in players if x[1].side == GOOD]
    embed = discord.Embed(
        title="게임 종료",
        description=("선" if win_side == GOOD else "악") + "이 이겼습니다.",
        colour=discord.Colour.red() if win_side == EVIL else discord.Colour.blue()
    )
    for i in good_players:
        embed.add_field(name=i[1].name_kr, value=f"<@{i[0].id}>" if good_players else "-")
    for i in evil_players:
        embed.add_field(name=i[1].name_kr, value=f"<@{i[0].id}>" if evil_players else "-")

    await channel.send("게임이 종료되었습니다.", embed=embed)

async def avalon_help(channel:discord.TextChannel):
    embed1 = discord.Embed(
        title="레지스탕스: 아발론",
        description="<레지스탕스: 아발론>은 각자의 정체를 숨긴 채 임무를 수행하는 게임입니다.\n\n누군가는 `아서 왕의 충성스러운 신하`가 되어 선과 명예를 위해 싸우고,\n\n누군가는 `모드레드의 수하`가 되어 모드레드를 좇아 악을 행합니다.\n\n선은 원정이 3번 성공해야 승리하고, 악은 원정이 3번 실패해야 승리합니다.\n\n원정이 3번 승리하더라도 악이 멀린을 암살하면 악이 승리합니다.",
        colour=discord.Colour.gold()
    )
    embed2 = discord.Embed(
        title="게임 진행",
        description="게임은 총 5라운드이며, 각 라운드는 `원정대 구성`단계와 `원정 진행`단계로 나뉩니다.",
        colour=discord.Colour.gold()
    )
    embed2.add_field(name="원정대 구성", value="원정대를 구성할 기사를 지목합니다.\n\n모든 플레이어는 대표의 구성안에 대해 투표하여\n\n원정대를 확정하거나 변경할 수 있습니다.\n\n투표는 과반수가 넘어야 하며, 동률일 경우 거부됩니다.\n\n", inline=False)
    embed2.add_field(name="원정 진행",value="원정대에 소속된 플레이어들이 원정의 성공여부를 결정합니다.\n\n원정대의 모든 인원이 성공에 투표해야 원정에 성공합니다.\n\n단, 7명 이상 게임에서는 4번째 원정이 실패하려면 2명이 실패에 투표해야 합니다.\n\n", inline=False)

    embed3 = discord.Embed(
        title="게임 종료",
        description="원정이 총 세 번 실패하면 즉시 악의 승리로 게임이 종료됩니다.\n\n원정대 구성안이 한 라운드에 5번 연속 거부당해도 즉시 악의 승리로 게임이 끝납니다.\n\n하지만 원정이 3번 성공한다고 해도 선이 즉시 승리하지는 않습니다.",
        colour=discord.Colour.gold()
    )
    embed3.add_field(name="멀린 암살 시도", value="원정이 총 3번 성공하면, 악은 최후의 발악으로서 `멀린 암살`을 시도합니다.\n\n악 플레이어들끼리 멀린이 누구일지 논의한 뒤, 멀린이라고 추측되는 플레이어를 암살자가 지목합니다.\n\n지목된 플레이어가 멀린이면 악이 승리하고, 그렇지 않으면 선이 승리합니다.\n\n")

    embed4 = discord.Embed(
        title="캐릭터 소개",
        colour=discord.Colour.gold()
    )
    embed4.add_field(name="멀린 (선)", value="악이 누구인지 봅니다. 정체가 들키게 되면 `암살 시도` 단계에서 암살당할 수 있습니다.", inline=False)
    embed4.add_field(name="퍼시벌 (선)", value="`멀린`이 누구인지 봅니다.",inline=False)
    embed4.add_field(name="암살자 (악)", value="`암살 시도` 시 목표를 지목합니다.",inline=False)
    embed4.add_field(name="오베론 (악)", value="다른 악과 서로 정체를 모릅니다.",inline=False)
    embed4.add_field(name="모르가나 (악)", value="`퍼시벌`이 보기에 멀린처럼 보입니다.", inline=False)
    embed4.add_field(name="모드레드 (악)", value="`멀린`에게 정체를 보여주지 않습니다.", inline=False)
    await channel.send(embed=embed1)
    await channel.send(embed=embed2)
    await channel.send(embed=embed3)
    await channel.send(embed=embed4)

async def avalon_end_judge(client:discord.Client, channel:discord.TextChannel, participants:deque, total_quest_stat:list):
    await channel.send(embed=await avalon_board_embed(total_quest_stat))
    if total_quest_stat.count(0) >= 3:
        await avalon_end(channel, participants, EVIL)
        return True
    if total_quest_stat.count(1) == 3:
        result = await avalon_assassinate(client, channel, participants)
        if result:
            await avalon_end(channel, participants, EVIL)
            return True
        else:
            await avalon_end(channel, participants, GOOD)
            return True
    return False

async def avalon_get_setupcode(client:discord.Client, channel:discord.TextChannel, starter):
    embed = discord.Embed(
        title="게임 구성",
        description="1. 기본 (멀린, 암살자)\n\n2. 약간 추가 (멀린, 암살자, 모르가나, 퍼시벌)\n\n3. 약간 추가 (멀린, 암살자, 모드레드, 퍼시벌)\n\n4. 많이 추가 (멀린, 암살자, 모드레드, 퍼시벌, 오베론)",
        colour=discord.Colour.gold()
    )
    await channel.send("게임 구성을 입력해주세요.", embed=embed)
    def check(m):
        return m.content in ['1', '2', '3', '4'] and m.author == starter and m.channel == channel
    setup_code_msg = await client.wait_for("message", check=check)
    setup_code = int(setup_code_msg.content)
    await setup_code_msg.delete()
    return setup_code

async def avalon(client:discord.Client, channel:discord.TextChannel, starter):
    # type(participants) -> collections.Deque (RANDOMLY SHUFFLED)
    participants = await avalon_get_participants(client, channel, starter)
    if participants == None:
        return
    setup_code = await avalon_get_setupcode(client, channel, starter)

    "Setup phase"
    participants = await avalon_setup(channel, deque([x for x in participants]), setup_code)
    total_quest_stat = [-1] * 5
    "===== repeat below - 5 times ====="
    for i in range(5):
        await avalon_setup_turn_announce(channel, participants, False)
        valid = await avalon_end_judge(client, channel, participants, total_quest_stat)
        if valid:
            return
        vote_fail_cnt = 0
        while 1:
            if vote_fail_cnt == 5:
                await avalon_end(channel, participants, EVIL)
                return
            "team_building phase"

            quest_member = await avalon_build_quest_team(client, channel, participants, i)
            vote_success = await avalon_vote_quest_team(client, channel, quest_member, participants, vote_fail_cnt)
            if vote_success:
                break
            else:
                vote_fail_cnt += 1
        "Quest phase"
        quest_success = await avalon_quest(client, channel, quest_member, [x for x in participants], i)
        total_quest_stat[i] = 1 if quest_success else 0
    await avalon_end_judge(client, channel, participants, total_quest_stat)

# returns set of participants
async def avalon_get_participants(client:discord.Client, channel:discord, author):
    return await game.get_participants("아발론", client, channel, author, 5, 10)