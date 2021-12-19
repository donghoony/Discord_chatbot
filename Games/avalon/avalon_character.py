"AVALON CHARACTERS"
GOOD = 1
EVIL = 0

minions_url = ["https://i.imgur.com/6KtaHE1.png","https://i.imgur.com/E8mR01p.png","https://i.imgur.com/ketz7u7.png",]
servants_url = ["https://i.imgur.com/hmZ4yxb.png","https://i.imgur.com/bKUXXxg.png","https://i.imgur.com/4agzoQh.png",
                "https://i.imgur.com/v4XpAXM.png","https://i.imgur.com/hmZ4yxb.png"]


class AvalonCharacter:
    pass

class Merlin(AvalonCharacter):
    def __init__(self):
        self.name_en = "Merlin"
        self.name_kr = "멀린"
        self.side = GOOD
        self.description = "모든 것을 깨우친 단 한 명, 멀린.\n악이 누구인지 파악할 수 있으나,\n악에게 자신의 정체를 들킨다면 패배한다"
        self.url = "https://i.imgur.com/RYwoMXb.png"

class MinionsOfMordred(AvalonCharacter):
    def __init__(self, index):
        self.name_en = "Minions of Mordred"
        self.name_kr = "모드레드의 수하"
        self.side = EVIL
        self.description = "모드레드를 좇아 악을 행하는 모드레드의 수하"
        self.url = minions_url[index]

class ArthursServants(AvalonCharacter):
    def __init__(self, index):
        self.name_en = "Arthur's Servants"
        self.name_kr = "아서 왕의 충성스러운 신하"
        self.side = GOOD
        self.description = "선과 명예를 위해 싸우는 아서 왕의 충성스러운 신하"
        self.url = servants_url[index]

class Assassin(AvalonCharacter):
    def __init__(self):
        self.name_en = "Assassin"
        self.name_kr = "암살자"
        self.side = EVIL
        self.description = "숨어있는 멀린을 찾아 숨통을 끊으면 승리할 것이다."
        self.url = "https://i.imgur.com/wQESbg4.png"

class Mordred(AvalonCharacter):
    def __init__(self):
        self.name_en = "Mordred"
        self.name_kr = "모드레드"
        self.side = EVIL
        self.description = "게임이 시작될 때 멀린에게 자신의 정체를 밝히지 않는다."
        self.url = "https://i.imgur.com/zoDUlO3.png"

class Morgana(AvalonCharacter):
    def __init__(self):
        self.name_en = "Morgana"
        self.name_kr = "모르가나"
        self.side = EVIL
        self.description = "겉보기에는 멀린으로 보인다.\n(퍼시벌은 멀린이 두 명으로 보인다)"
        self.url = "https://i.imgur.com/izElhnN.png"

class Percival(AvalonCharacter):
    def __init__(self):
        self.name_en = "Percival"
        self.name_kr = "퍼시벌"
        self.side = GOOD
        self.description = "게임 시작 시 멀린이 누구인지 확인한다."
        self.url = "https://i.imgur.com/gRoMpZV.png"

class Oberon(AvalonCharacter):
    def __init__(self):
        self.name_en = "Oberon"
        self.name_kr = "오베론"
        self.side = EVIL
        self.description = "악하지만 모드레드의 수하는 아니다.\n오베론과 다른 악 플레이어들은 서로의 정체를 모른다."
        self.url = "https://i.imgur.com/gIoJgH8.png"
