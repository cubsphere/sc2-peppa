import random

import sc2
from sc2 import Race
from sc2.constants import *
from sc2.player import Bot

class ConstrutorEconomico():
    def __init__(self, bot):
        self.__bot = bot

    def active_mineral_patches(self):
        return self.__bot.units(NEXUS).amount * 6

    def active_vespene_geysers(self):
        return self.__bot.units(ASSIMILATOR).ready.amount

    def utility(self):
        return self.__bot.workers.amount / 24.0


    async def run(self, iteration):
        # redistribute
        if iteration % 10 == 0:
            await self.__bot.distribute_workers()
        # supply pylon
        if self.__bot.supply_left < 4 + self.__bot.supply_used // 25 and self.__bot.can_afford(PYLON) and self.__bot.units(PYLON).not_ready.amount < 1 + self.__bot.supply_used // 70:
            if self.__bot.units(NEXUS).exists:
                await self.__bot.build(PYLON, near=self.__bot.units(NEXUS).random.position.random_on_distance(random.randrange(8, 11)))
        # hard cap at 60 workers
        if self.__bot.can_afford(PROBE) and self.__bot.workers.amount < 60 and self.__bot.workers.amount < (self.active_mineral_patches() + self.active_vespene_geysers()) * 3:
            for nexus in self.__bot.units(NEXUS).ready:
                if self.__bot.can_afford(PROBE) and nexus.is_idle:
                    await self.__bot.do(nexus.train(PROBE))
        # vespene
        if (self.__bot.minerals > 500 and self.__bot.vespene < 100) or (self.__bot.units(ASSIMILATOR).amount < 1 and self.__bot.can_afford(ASSIMILATOR)):
            for nexus in self.__bot.units(NEXUS).ready:
                vgs = self.__bot.state.vespene_geyser.closer_than(10.0, nexus)
                for vg in vgs:
                    worker = self.__bot.select_build_worker(vg.position)
                    if worker is None:
                        break
    
                    if not self.__bot.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                        await self.__bot.do(worker.build(ASSIMILATOR, vg))
                        break
        # expansion
        if self.__bot.units(NEXUS).amount < 2 and (self.active_mineral_patches() + self.active_vespene_geysers()) * 3 - self.__bot.workers.amount < 4 * self.__bot.units(NEXUS).amount - 2:
            await self.__bot.expand_now()

