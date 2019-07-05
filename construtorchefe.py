import sc2
from sc2.player import Bot
from construtoreconomico import *
from construtormilitar import *

class ConstrutorChefe():
    def __init__(self, bot):
        self.__bot = bot
        self.__econ = ConstrutorEconomico(bot)
        self.__mil = ConstrutorMilitar(bot)

    async def run(self, iteration):
        # redistribute
        if iteration % 10 == 0:
            await self.__bot.distribute_workers()
        # supply pylon
        if self.__bot.supply_left < 4 + self.__bot.supply_used // 25 and self.__bot.can_afford(PYLON) and self.__bot.units(PYLON).not_ready.amount < 1 + self.__bot.supply_used // 70:
            if self.__bot.units(NEXUS).exists:
                await self.__bot.build(PYLON, near=self.__bot.units(NEXUS).random.position.random_on_distance(random.randrange(8, 11)))
        
        #print (self.__econ.utility())
        #print (self.__mil.utility())
        #print ()
        if self.__econ.utility() < self.__mil.utility():
            await self.__econ.run(iteration)
            await self.__mil.run(iteration)
        else:
            await self.__mil.run(iteration)
            await self.__econ.run(iteration)
