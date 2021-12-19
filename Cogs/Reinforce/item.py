from math import log
from random import randint

class Item():
    def __init__(self, owner_id, name):
        self.name = name
        self.owner_id = owner_id
        self.level = 1
        self.reinforced_count = 0
        self.maximum_level = 0
        self.broken_count = 0

    def _upgrade_item(self, amount):
        self.level += amount
        self.reinforced_count += 1
        self.maximum_level = max(self.maximum_level, self.level)

    def _downgrade_item(self, amount):
        # returns True if item is broken
        if self.level > amount:
            self.level -= amount
        else:
            self.level = 1
        self.reinforced_count += 1
        if self._chance_break_item():
            return True
        return False

    def _chance_break_item(self):
        # odds of breaking items when it fails to reinforce:
        # 0 ~ 7.5 by level
        # self.level / 100
        chance = min(self.level / 100, 7.5)
        if self._random_hammer(chance):
            self.level = 1
            self.broken_count += 1
            return True
        return False

    def _reinforce_item(self):
        odd = self._odd_function(self.level)
        before_level = self.level
        result = self._random_hammer(odd) # True, False
        amount = self._random_level()
        if result:
            self._upgrade_item(amount)
            after_levels = self._multiple_upgrade()
        else:
            if self._downgrade_item(amount):
                result = 2
            after_levels = [self.level]
        return result, odd, before_level, after_levels

    def _multiple_upgrade(self):
        ret = [self.level]
        odd = 12
        while self._random_hammer(odd):
            up = self._random_level()
            self._upgrade_item(up)
            ret.append(self.level)
        return ret

    def _odd_function(self, level):
        if level <= 192:
            return round(3068000/(level-4000) + 867, 2)
        else:
            return round(100 - log((level-2)**3 + 2, 1.5), 2)

    def _random_level(self):
        return randint(1, 9)

    def _random_hammer(self, percentage):
        user_number = randint(1, 10000)
        return 1 if user_number <= percentage * 100 else 0

