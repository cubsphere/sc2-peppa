from sc2 import Race
from sc2.constants import *
from sc2.player import Bot

class Energia():
    def __init__(self, bot):
        self.__bot = bot

    async def run(self, iteration):
        if self.__bot.units(NEXUS).ready.exists:
            await self.spend_energy(self.__bot.units(NEXUS).ready.random)

    async def get_target(self):
        # cyber core
        if self.__bot.units(CYBERNETICSCORE).ready.exists:
            building = self.__bot.units(CYBERNETICSCORE).ready.first
            if not building.is_idle and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                return building
        # forge
        for building in self.__bot.units(FORGE).ready:
            if not building.is_idle and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                return building
        # council
        for building in self.__bot.units(TWILIGHTCOUNCIL).ready:
            if not building.is_idle and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                return building
        # robo
        for building in self.__bot.units(ROBOTICSFACILITY).ready:
            if not building.is_idle and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                return building
        # nexus
        for building in self.__bot.units(NEXUS).ready:
            if not building.is_idle and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                return building
        # warpgates
        for building in self.__bot.units(WARPGATE).ready:
            abilities = await self.__bot.get_available_abilities(building)
            if len(abilities) < 1 and not building.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                return building

    async def spend_energy(self, nexus, target=None):
        if target and target.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            target = None
        abilities = await self.__bot.get_available_abilities(nexus)
        if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
            if not target:
                target = await self.get_target()
            if target:
                await self.__bot.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, target))