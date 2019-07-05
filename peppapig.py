import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from construtorchefe import *
from energia import *
from marechal import *

class PeppaPigBot(sc2.BotAI):
    def __init__(self):
        self.__energia = Energia(self)
        self.__construtor = ConstrutorChefe(self)
        self.__marechal = Marechal(self)
        # temporary
        self.proxy_built = False

    def select_target(self):
        return self.enemy_start_locations[0]

    async def on_step(self, iteration):
        self.military = self.units(STALKER).ready | self.units(ZEALOT).ready | self.units(SENTRY).ready | self.units(IMMORTAL).ready
        self.scout = self.units(PHOENIX) | self.units(ADEPT)
        await self.__energia.run(iteration)
        await self.__construtor.run(iteration)
        await self.__marechal.run(iteration)

        # build proxy pylon
        if self.units(CYBERNETICSCORE).amount >= 1 and not self.proxy_built and self.can_afford(PYLON):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
            await self.build(PYLON, near=p)
            self.proxy_built = True

        
def main():
    sc2.run_game(sc2.maps.get("CyberForestLE"), [
        Bot(Race.Protoss, PeppaPigBot()),
        Computer(Race.Protoss, Difficulty.VeryHard)
    ], realtime=False)

if __name__ == '__main__':
    main()