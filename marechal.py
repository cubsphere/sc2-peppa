import sc2
from sc2.player import Bot
from sc2 import Race, Difficulty
from sc2.constants import *
from soldado import *
from order import *

class Marechal():
    def __init__(self, bot):
        self.__bot = bot
        self.__soldados = []

    def select_target(self):
        return self.__bot.enemy_start_locations[0]

    async def run(self, iteration):
        # run para soldados
        new_soldados = []
        for unit in self.__bot.military | self.__bot.scout:
            found = False
            for soldado in self.__soldados:
                if unit.tag == soldado.tag:
                    await soldado.run(iteration, unit, self.__bot)
                    new_soldados.append(soldado)
                    found = True
            if not found:
                soldado = Soldado(unit)
                await soldado.run(iteration, unit, self.__bot)
                new_soldados.append(soldado)
        self.__soldados = new_soldados
        # temporary attack
        # attack
        if self.__bot.units(STALKER).amount > 10:
            for soldado in self.__soldados:
                if soldado.order == Order.Defend:
                    soldado.order = Order.Attack
                    soldado.target = self.select_target()
        elif self.__bot.units(STALKER).amount > 6:
            for soldado in self.__soldados:
                if soldado.order == Order.Defend:
                    soldado.target = self.__bot.game_info.map_center.towards(self.select_target(), 20)