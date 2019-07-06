import random

import sc2
from sc2 import Race
from sc2.constants import *
from sc2.player import Bot
from future.backports.http.client import GATEWAY_TIMEOUT

class ConstrutorMilitar():
    def __init__(self, bot):
        self.__bot = bot
        self.__warpgate = False

    def utility(self):
        seconds = min (540, self.__bot.time)
        if (seconds < 30):
            return 0
        if (seconds < 60 and self.__bot.units(GATEWAY).amount < 1):
            return 1
        if (seconds < 180 and self.__bot.units(GATEWAY).amount >= 1):
            if (self.__bot.units(CYBERNETICSCORE).amount >= 1):
                return 0
            else:
                return 1
        gateway_normalized_difference = min (154, (seconds - self.__bot.units(GATEWAY).amount * 77)) / 154
        if self.__bot.units(GATEWAY).amount == 7:
            gateway_normalized_difference = 0

        units_normalized_difference = 0
        stalker_count = self.__bot.units(STALKER).amount
        zealot_count = self.__bot.units(ZEALOT).amount
        sentry_count = self.__bot.units(SENTRY).amount
        unit_count = stalker_count + zealot_count + sentry_count
        if (seconds > 180 and seconds < 210):
            units_normalized_difference = min (60, ((seconds - 180) - unit_count * 20)) / 40
        if (seconds >= 210):
            units_normalized_difference = 1

        return max(gateway_normalized_difference, units_normalized_difference)

    async def run(self, iteration):
        if self.__bot.units(PYLON).ready.exists:
            #to not get a proxyPylon randomically 
            nexus = self.__bot.units(NEXUS).ready.random
            pylonNotProxy = self.__bot.units(PYLON).ready.closer_than(25.0, nexus)
            #random in pylonNotProxy
            if pylonNotProxy.exists:
                pylon = pylonNotProxy.random
            else:
                pylon = self.__bot.units(PYLON).random
            proxy = self.__bot.units(PYLON).ready.closest_to(self.__bot.select_target())
            # buildings
            # gates
            if self.__bot.units(GATEWAY).ready.exists and not self.__bot.units(CYBERNETICSCORE).exists and self.__bot.can_afford(CYBERNETICSCORE):
                await self.__bot.build(CYBERNETICSCORE, near=pylon)
            if (self.__bot.time < 180 and self.__bot.units(WARPGATE).amount + self.__bot.units(GATEWAY).amount > 0):
                return
            if (min(500, self.__bot.units(WARPGATE).amount + self.__bot.units(GATEWAY).amount) * 160) < self.__bot.minerals and self.__bot.can_afford(GATEWAY) and self.__bot.supply_used < 130:
                await self.__bot.build(GATEWAY, near=pylon)
            # forge
            if (self.__bot.units(FORGE).amount < 1 and self.__bot.can_afford(FORGE) and self.__bot.time > 180):
                await self.__bot.build(FORGE, near=pylon)
            for forge in self.__bot.units(FORGE).ready:
                if forge.is_idle:
                    targetAbilities = [RESEARCH_CHARGE, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, FORGERESEARCH_PROTOSSSHIELDSLEVEL1, FORGERESEARCH_PROTOSSSHIELDSLEVEL2, FORGERESEARCH_PROTOSSSHIELDSLEVEL3]
                    abilities = await self.__bot.get_available_abilities(forge)
                    for upgrade in targetAbilities:
                        if (upgrade in abilities) and self.__bot.can_afford(upgrade):
                            err = await self.__bot.do(forge(upgrade))
                            if not err:
                                break
            # robo
            if self.__bot.can_afford(ROBOTICSFACILITY) and self.__bot.units(NEXUS).ready.amount - 1 > self.__bot.units(ROBOTICSFACILITY).amount:
                await self.__bot.build(ROBOTICSFACILITY, near=pylon)
            # tech

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
            if not self.__warpgate and self.__bot.units(CYBERNETICSCORE).ready.exists and self.__bot.can_afford(RESEARCH_WARPGATE):
                ccore = self.__bot.units(CYBERNETICSCORE).ready.first
                abilities = await self.__bot.get_available_abilities(ccore)
                if AbilityId.RESEARCH_WARPGATE in abilities:
                    await self.__bot.do(ccore(RESEARCH_WARPGATE))
            # robo
            for robo in self.__bot.units(ROBOTICSFACILITY).ready:
                if robo.is_idle and self.__bot.can_afford(IMMORTAL):
                    print('trying immortal')
                    await self.__bot.do(robo.train(IMMORTAL))


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
                pos = pylon.position.to2.random_on_distance(random.uniform(2, 4))
                placement = await self.__bot.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    #return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                await self.__bot.do(warpgate.warp_in(unit, placement))