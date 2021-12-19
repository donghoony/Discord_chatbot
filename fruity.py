# -*- coding: utf-8 -*

def init():
    from discord.ext import commands
    import discord
    from discord_slash import SlashCommand
    from os import walk

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
    slash = SlashCommand(bot, sync_commands=True)

    unloadCogList = ["voiceclientcog.py"]
    print("Loading Cogs: (", end="")
    for root, subdirs, files in walk('./Cogs'):
        root = root.replace("\\", ".", -1)
        for f in files:
            if f.endswith('cog.py') and f not in unloadCogList:
                bot.load_extension(f"{root[2:]}.{f[:-3]}")
                print(f"{root[2:]}.{f[:-3]}, ", end="")
    print(")")

    @bot.event
    async def on_ready():
        print(f"BOT ID: {bot.user.id}")
        print("===BOT READY===")
        cur_status = discord.Game("개발")
        await bot.change_presence(status=discord.Status.online, activity=cur_status)

    @bot.event
    async def on_message(message):
        await bot.process_commands(message)
        return

    return bot

if __name__ == "__main__":
    from chatbot_secrets import DISCORD_TOKEN
    bot = init()
    bot.run(DISCORD_TOKEN)
