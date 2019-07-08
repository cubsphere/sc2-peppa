import sc2
from sc2.player import Bot
from construtoreconomico import *
from construtormilitar import *

class ConstrutorChefe():
    def __init__(self, bot):
        self.__bot = bot
        self.__econ = ConstrutorEconomico(bot)
        self.__mil = ConstrutorMilitar(bot)

    def is_good_location(self, position):
        return not self.__bot.state.mineral_field.closer_than(3, position).exists and not self.__bot.units.structure.closer_than(3, position).exists

    async def run(self, iteration):
        # redistribute
        if iteration % 10 == 0:
            await self.__bot.distribute_workers()
        # supply pylon
        if self.__bot.supply_left < 4 + self.__bot.supply_used // 25 and self.__bot.can_afford(PYLON) and self.__bot.units(PYLON).not_ready.amount < 1 + self.__bot.supply_used // 70:
            pivot = self.__bot.start_location
            if self.__bot.units(NEXUS).exists:
                pivot = self.__bot.units(NEXUS).random.position
            pos = pivot
            for i in range(5):
                pos = pivot.random_on_distance(random.randrange(8, 15))
                if self.is_good_location(pos):
                    break
            if self.is_good_location(pos):
                await self.__bot.build(PYLON, near=pos)
        econ_util = self.__econ.utility()
        mil_util = self.__mil.utility()
        print (econ_util)
        print (mil_util)
        print ()
        if econ_util < mil_util:
            await self.__mil.run(iteration)
            await self.__econ.run(iteration)
        elif econ_util < 1.8 and self.__bot.minerals < 450:
            await self.__econ.run(iteration)
            await self.__mil.run(iteration)
        else:
            await self.__econ.run(iteration)
