import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class PeppaPigBot(sc2.BotAI):

    def __init__(self):
        self.warpgate_started = False
        self.proxy_built = False

    def select_target(self, state):
        return self.enemy_start_locations[0]

    async def warp_new_units(self, proxy):
        for warpgate in self.units(WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            # all the units have the same cooldown anyway so let's just look at ZEALOT
            if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                pos = proxy.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    #return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                await self.do(warpgate.warp_in(STALKER, placement))

    async def spend_energy(self, nexus):
        if not self.units(CYBERNETICSCORE).ready.exists:
            if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))
        else:
            ccore = self.units(CYBERNETICSCORE).ready.first
            if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))

    async def manage_supply(self, nexus):
        if self.supply_left < 2 and not self.already_pending(PYLON):
            if self.can_afford(PYLON):
                await self.build(PYLON, near=nexus)
                return

    async def on_step(self, iteration):
        await self.distribute_workers()

        if not self.units(NEXUS).ready.exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return
        else:
            nexus = self.units(NEXUS).ready.random

        if self.workers.amount >= 16 and self.units(NEXUS).amount == 1:
            print('expanding!')
            await self.expand_now()

        # build supply pylons
        await self.manage_supply(nexus)

        # building probes
        if self.workers.amount < self.units(NEXUS).amount*22 and nexus.is_idle:
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))
        # 
        elif self.units(PYLON).amount < 5 and not self.already_pending(PYLON) and self.supply_left <= 5:
            if self.can_afford(PYLON):
                await self.build(PYLON, near=nexus.position.towards(self.game_info.map_center, 5))


        # simple building
        if self.units(PYLON).ready.exists:
            proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists:
                if not self.units(CYBERNETICSCORE).exists:
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)
            if self.can_afford(GATEWAY) and self.units(WARPGATE).amount + self.units(GATEWAY).amount < 2 + 5 * (self.units(NEXUS).amount - 1):
                await self.build(GATEWAY, near=pylon)

        # vespene gas
        for nexus in self.units(NEXUS).ready:
            vgs = self.state.vespene_geyser.closer_than(10.0, nexus)
            for vg in vgs:
                if not self.can_afford(ASSIMILATOR):
                    break

                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                    await self.do(worker.build(ASSIMILATOR, vg))

        # warp gate research
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(RESEARCH_WARPGATE) and not self.warpgate_started:
            ccore = self.units(CYBERNETICSCORE).ready.first
            await self.do(ccore(RESEARCH_WARPGATE))
            self.warpgate_started = True

        # morph gateways into warpgates
        for gateway in self.units(GATEWAY).ready:
            abilities = await self.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
                await self.do(gateway(MORPH_WARPGATE))

        # warp units in proxy pylon
        if self.proxy_built and self.workers.amount >= 30:
            await self.warp_new_units(proxy)

        # attack
        if self.units(STALKER).amount > 10:
            for vr in self.units(STALKER).ready.idle:
                await self.do(vr.attack(self.select_target(self.state)))
            for vr in self.units(ZEALOT).ready.idle:
                await self.do(vr.attack(self.select_target(self.state)))

        # build proxy pylon
        if self.units(CYBERNETICSCORE).amount >= 1 and not self.proxy_built and self.can_afford(PYLON):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
            await self.build(PYLON, near=p)
            self.proxy_built = True

        await self.spend_energy(nexus)


def main():
    sc2.run_game(sc2.maps.get("CyberForestLE"), [
        Bot(Race.Protoss, PeppaPigBot()),
        Computer(Race.Protoss, Difficulty.Hard)
    ], realtime=False)

if __name__ == '__main__':
    main()
