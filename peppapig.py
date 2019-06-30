import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from construtorchefe import *
from energia import *

class PeppaPigBot(sc2.BotAI):
    def __init__(self):
        self.__energia = Energia(self)
        self.__construtor = ConstrutorChefe(self)
        # temporary
        self.proxy_built = False

    def select_target(self):
        return self.enemy_start_locations[0]

    async def on_step(self, iteration):
        await self.__energia.run(iteration)
        await self.__construtor.run(iteration)

        # temporary attack
        # attack
        if self.units(STALKER).amount > 10:
            for vr in self.units(STALKER).ready.idle | self.units(ZEALOT) | self.units(SENTRY) | self.units(ADEPT):
                await self.do(vr.attack(self.select_target()))

        # build proxy pylon
        if self.units(CYBERNETICSCORE).amount >= 1 and not self.proxy_built and self.can_afford(PYLON):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
            await self.build(PYLON, near=p)
            self.proxy_built = True
def main():
    sc2.run_game(sc2.maps.get("CyberForestLE"), [
        Bot(Race.Protoss, PeppaPigBot()),
        Computer(Race.Zerg, Difficulty.VeryHard)
    ], realtime=False)

if __name__ == '__main__':
    main()