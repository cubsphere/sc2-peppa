import random

import sc2
from sc2 import Race
from sc2.constants import *
from sc2.player import Bot

class ConstrutorMilitar():
    def __init__(self, bot):
        self.__bot = bot
        self.__warpgate = False

    def utility(self):
        return 1.5

    async def run(self, iteration):
        if self.__bot.units(PYLON).ready.exists:
            pylon = self.__bot.units(PYLON).ready.random
            proxy = self.__bot.units(PYLON).ready.closest_to(self.__bot.select_target())
            # production
            # gateway
            for gate in self.__bot.units(GATEWAY).ready:
                adept = self.__bot.units(ADEPT).amount < 3
                if gate.is_idle:
                    if self.__warpgate:
                        await self.__bot.do(gate(MORPH_WARPGATE))
                    else:
                        abilities = await self.__bot.get_available_abilities(gate)
                        if AbilityId(MORPH_WARPGATE) in abilities:
                            self.__warpgate = True
                            await self.__bot.do(gate(MORPH_WARPGATE))
                        # elif adept and AbilityId(TRAIN_ADEPT) in abilities and self.__bot.can_afford(ADEPT):
                            #await self.__bot.do(gate(TRAIN_ADEPT))
            await self.warp_new_units(proxy)
            await self.warp_new_units(pylon)
            # warpgate
            if self.__bot.units(GATEWAY).ready.exists and not self.__bot.units(CYBERNETICSCORE).exists and self.__bot.can_afford(CYBERNETICSCORE):
                await self.__bot.build(CYBERNETICSCORE, near=pylon)
            if not self.__warpgate and self.__bot.units(CYBERNETICSCORE).ready.exists and self.__bot.can_afford(RESEARCH_WARPGATE):
                ccore = self.__bot.units(CYBERNETICSCORE).ready.first
                abilities = await self.__bot.get_available_abilities(ccore)
                if AbilityId.RESEARCH_WARPGATE in abilities:
                    await self.__bot.do(ccore(RESEARCH_WARPGATE))
            # robo

            # buildings
            # gates
            if (self.__bot.units(WARPGATE).amount + self.__bot.units(GATEWAY).amount) * 160 < self.__bot.minerals and self.__bot.can_afford(GATEWAY):
                await self.__bot.build(GATEWAY, near=pylon)
            # forge
            if (self.__bot.units(FORGE).amount < 2 and self.__bot.minerals > 500 and self.__bot.vespene > 400):
                await self.__bot.build(FORGE, near=pylon)
            for forge in self.__bot.units(FORGE).ready:
                targetAbilities = [RESEARCH_CHARGE, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, FORGERESEARCH_PROTOSSSHIELDSLEVEL1, FORGERESEARCH_PROTOSSSHIELDSLEVEL2, FORGERESEARCH_PROTOSSSHIELDSLEVEL3]
                abilities = await self.__bot.get_available_abilities(forge)
                for upgrade in targetAbilities:
                    if (upgrade in abilities) and self.__bot.can_afford(upgrade):
                        err = await self.__bot.do(forge(upgrade))
                        if not err:
                            break
            # robo

            # tech

    async def warp_new_units(self, pylon):
        for warpgate in self.__bot.units(WARPGATE).ready:
            if self.__bot.supply_used > 60 and self.__bot.minerals <= 400:
                return
            abilities = await self.__bot.get_available_abilities(warpgate)
            if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                unit = None
                if self.__bot.can_afford(STALKER):
                    unit = STALKER
                elif self.__bot.can_afford(ZEALOT):
                    unit = ZEALOT
                elif self.__bot.can_afford(SENTRY):
                    unit = SENTRY
                if not unit:
                    return
                # all the units have the same cooldown anyway so let's just look at ZEALOT
                pos = pylon.position.to2.random_on_distance(4)
                placement = await self.__bot.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    #return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                await self.__bot.do(warpgate.warp_in(unit, placement))