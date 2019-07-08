import random

import sc2
from sc2 import Race
from sc2.constants import *
from sc2.player import Bot

class ConstrutorEconomico():
    def __init__(self, bot):
        self.__bot = bot

    def active_mineral_patches(self):
        ans = 0
        for patch in self.__bot.state.mineral_field:
            if self.__bot.units(NEXUS).closer_than(8, patch).exists:
                ans = ans + 1
        #print(ans, ' patches')
        return ans

    def active_vespene_geysers(self):
        return self.__bot.units(ASSIMILATOR).ready.amount

    def utility(self):
        seconds = min(576, self.__bot.time)
        if (seconds > 60 and self.__bot.units(NEXUS).amount < 2):
            return 2
        workers = self.__bot.workers.amount
        expected_workers = (self.active_mineral_patches() * 2.3 + self.active_vespene_geysers() * 3)
        normalized_difference = (workers - expected_workers + 10) / 10
        return normalized_difference


    async def run(self, iteration):
        # hard cap at 60 workers
        if self.__bot.can_afford(PROBE) and self.__bot.workers.amount < 60 and self.__bot.workers.amount < (self.active_mineral_patches() * 2.3 + self.active_vespene_geysers() * 3):
            for nexus in self.__bot.units(NEXUS).ready:
                if self.__bot.can_afford(PROBE) and nexus.is_idle:
                    await self.__bot.do(nexus.train(PROBE))
        # vespene
        if (self.__bot.minerals > 400 and self.__bot.vespene < 100) or (self.__bot.units(ASSIMILATOR).amount < 1 and self.__bot.can_afford(ASSIMILATOR)):
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
        if self.utility() > 0.8:
            await self.__bot.expand_now()

