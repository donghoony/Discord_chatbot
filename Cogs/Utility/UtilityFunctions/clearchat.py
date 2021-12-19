async def clear(ctx):
    message = ctx.message
    try:
        cnt = int(message.content.split(" ")[1]) + 1
    except ValueError:
        await message.channel.send("정확한 숫자를 입력해주세요. ex)`!clr 5`")
        return
    except IndexError:
        await message.channel.send("제거할 메시지 개수를 입력해주세요. ex)`!clr 5`")
        return
    if len(message.content.rstrip().split(" ")) != 2:
        await message.channel.send("제거할 메시지의 개수를 한 개만 입력해주세요. ex)`!clr 5`")
        return

    deleted = await message.channel.purge(limit=cnt)
    alert = await message.channel.send(f"{len(deleted)-1}개의 메시지를 삭제했습니다.")
    await alert.delete(delay=1.5)