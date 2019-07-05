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

    async def utility(self, position):
        return -position.distance_to(self.target)

    def find_target_unit_in_group(self, group, unit):
        sortedEnemies = group.sorted_by_distance_to(unit)
        target = sortedEnemies.first
        for enemy in sortedEnemies:
            if unit.target_in_range(enemy, 0):
                if enemy.health + enemy.shield < target.health + target.shield:
                    target = enemy
            else:
                break
        return target

    def nearby_target(self, bot, unit):
        if bot.state.enemy_units.exists:
            target_range = unit.sight_range
            nearbyEnemies = bot.state.enemy_units.closer_than(target_range, unit)
            if not nearbyEnemies.empty:
                target = self.find_target_unit_in_group(nearbyEnemies, unit)
                return unit.attack(target)
        return None

    async def run(self, iteration, unit, bot):
        print(unit)
        print(self.order)
        print(self.target)
        print(unit.position)
        print(iteration)
        print(self.last_order)
        if self.order == Order.Attack:
            if self.last_order + 10 < iteration:
                self.last_order = iteration
                if self.target.distance_to(unit) < 1:
                    self.order = Order.Patrol
                elif not self.attacking and unit.weapon_cooldown == 0:
                    if bot.state.enemy_units.exists:
                        order = self.nearby_target(bot, unit)
                        if order != None:
                            self.attacking = True
                            await bot.do(order)
                        else:
                            await bot.do(unit.attack(self.target.random_on_distance(4)))
                else:
                    bestEval = -98123789
                    bestPosition = self.target
                    for i in range(10):
                        randomPosition = unit.position.random_on_distance(random.uniform(0.5, 2))
                        curEval = await self.utility(randomPosition)
                        if curEval > bestEval:
                            bestEval = curEval
                            bestPosition = randomPosition
                    await bot.do(unit.move(bestPosition))
                    self.attacking = False
        elif self.order == Order.Defend:
            if self.last_order + 10 < iteration:
                self.last_order = iteration
                order = self.nearby_target(bot, unit)
                if order != None:
                    await bot.do(order)
                else:
                    await bot.do(unit.attack(self.target.random_on_distance(4)))
        elif self.order == Order.Patrol:
            if self.last_order + 40 < iteration:
                order = self.nearby_target(bot, unit)
                if order != None:
                    await bot.do(order)
                else:
                    await bot.do(unit.attack(self.target.random_on_distance(15)))
        elif self.order == Order.Scout:
            if self.last_order + 40 < iteration:
                self.last_order = iteration
                await bot.do(unit.move(self.target.random_on_distance(4)))
