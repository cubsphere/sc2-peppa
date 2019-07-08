import sc2
import random
from sc2.player import Bot
from sc2 import Race, Difficulty
from sc2.constants import *
from order import *

class Soldado():
    def __init__(self, unit):
        self.tag = unit.tag
        self.order = Order.Defend
        self.target = unit.position
        self.last_order = 0
        self.attacking = False
        self.role = Order.Defend

    async def utility(self, position):
        return -position.distance_to(self.target)

    def find_target_unit_in_group(self, group, unit):
        sortedEnemies = group.sorted_by_distance_to(unit)
        target = None
        for enemy in sortedEnemies:
            if unit.target_in_range(enemy, 0):
                if target == None:
                    target = enemy
                if enemy.health + enemy.shield < target.health + target.shield:
                    target = enemy
        return target

    def nearby_target(self, bot, unit):
        if bot.state.enemy_units.exists:
            target_range = unit.sight_range
            nearbyEnemies = bot.state.enemy_units.closer_than(target_range, unit)
            if not nearbyEnemies.empty:
                target = self.find_target_unit_in_group(nearbyEnemies, unit)
                if target == None:
                    return None
                return unit.attack(target)
        return None

    async def attack_pattern(self, iteration, unit, bot, exists_close):
        abilities = await bot.get_available_abilities(unit)
        if GUARDIANSHIELD_GUARDIANSHIELD in abilities:
            await bot.do(unit(GUARDIANSHIELD_GUARDIANSHIELD))
        if not exists_close:
            await bot.do(unit.attack(self.target))
        if self.target.distance_to(unit) < 1:
            self.order = Order.Patrol
        elif not self.attacking and unit.weapon_cooldown == 0:
            order = self.nearby_target(bot, unit)
            if order != None:
                self.attacking = True
                await bot.do(order)
            else:
                await bot.do(unit.attack(self.target.random_on_distance(4)))
        else:
            bestEval = -98123789
            bestPosition = self.target
            for i in range(50):
                randomPosition = unit.position.random_on_distance(random.uniform(0.5, 2))
                curEval = await self.utility(randomPosition)
                if curEval > bestEval:
                    bestEval = curEval
                    bestPosition = randomPosition
            if EFFECT_BLINK_STALKER in abilities:
                await bot.do(unit(EFFECT_BLINK_STALKER, bestPosition))
            await bot.do(unit.move(bestPosition))
            self.attacking = False

    async def run(self, iteration, unit, bot):
        #if 'Stalker' == unit.name:
        #print(unit.name)
        exists_close = bot.state.enemy_units.closer_than(unit.sight_range, unit).exists
        if self.order == Order.Attack:
            if self.last_order + 10 < iteration:
                self.last_order = iteration
                await self.attack_pattern(iteration, unit, bot, exists_close)
        elif self.order == Order.Defend:
            if self.last_order + 10 < iteration:
                self.last_order = iteration
                if exists_close:
                    await self.attack_pattern(iteration, unit, bot, exists_close)
                else:
                    await bot.do(unit.attack(self.target.random_on_distance(4)))
        elif self.order == Order.Patrol:
            if self.last_order + 40 < iteration:
                self.last_order = iteration
                if exists_close:
                    await self.attack_pattern(iteration, unit, bot, exists_close)
                else:
                    await bot.do(unit.attack(self.target.random_on_distance(15)))
        elif self.order == Order.Scout:
            if self.last_order + 20 < iteration:
                self.last_order = iteration
                if exists_close:
                    await self.attack_pattern(iteration, unit, bot, exists_close)
                else:
                    await bot.do(unit.move(self.target.random_on_distance(5)))
