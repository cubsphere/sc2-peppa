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
        if self.__econ.utility() < self.__mil.utility():
            await self.__econ.run(iteration)
            await self.__mil.run(iteration)
        else:
            await self.__mil.run(iteration)
            await self.__econ.run(iteration)
