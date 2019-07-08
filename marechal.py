import sc2
import random
from sc2.player import Bot
from sc2 import Race, Difficulty
from sc2.constants import *
from soldado import *
from order import *

class Marechal():
    def __init__(self, bot):
        self.__bot = bot
        self.__soldados = []
        self.__atk_pos = None
        self.__cur_pos = None
        self.__def_pos = None
        self.__def_cost = 0
        self.__last_time = -1000
        self.__defenders = 0
        self.__attackers = 0
        self.__request_proxy = False
        self.__atk_obs = 0
        self.__def_obs = 0

    def select_target(self):
        return self.__bot.enemy_start_locations[0]

    def get_scout_location(self):
        exp = []
        for center in self.__bot.expansion_locations:
            exp.append(center)
        for i in range(10):
            pos = random.choice(exp)
            if not self.__bot.state.enemy_units.closer_than(30, pos).exists and not self.__bot.units.closer_than(10, pos).exists:
                return pos
        return self.__bot.game_info.map_center.random_on_distance(20)

    async def run(self, iteration):
        if self.__last_time + 10 <= self.__bot.time:
            self.__last_time = self.__bot.time
            # atualizando posicao de ataque
            if self.__attackers > 20:
                # atacar base mais proxima da minha base
                special = self.__atk_pos == None
                self.__atk_pos = None
                best_dist = 129381
                for structure in self.__bot.state.enemy_units.structure:
                    if best_dist > structure.position.distance_to(self.__bot.start_location):
                        best_dist = structure.position.distance_to(self.__bot.start_location)
                        self.__atk_pos = structure.position
                if self.__atk_pos == None:
                    self.__atk_pos = self.__bot.enemy_start_locations[0]
            elif self.__attackers <= 8:
                self.__atk_pos = None
            if self.__atk_pos == None:
                self.__cur_pos = self.__def_pos
            else:
                self.__cur_pos = self.__cur_pos.towards(self.__atk_pos, min(self.__atk_pos.distance_to(self.__cur_pos), 20))
            # atualizando posicao de defesa
            # padrao
            self.__def_pos = self.__bot.main_base_ramp.top_center
            for nexus in self.__bot.units(NEXUS):
                new_pos = nexus.position.towards(self.__bot.game_info.map_center, 7)
                if new_pos.distance_to(self.__bot.game_info.map_center) < self.__def_pos.distance_to(self.__bot.game_info.map_center):
                    self.__def_pos = new_pos
            # por perigo
            self.__def_cost = 0
            for nexus in self.__bot.units(NEXUS):
                enemy_group = self.__bot.state.enemy_units.closer_than(20, nexus)
                if self.__def_cost < enemy_group.amount:
                    self.__def_cost = enemy_group.amount
                    self.__def_pos = enemy_group.center
            if self.__atk_pos != None:
                proxy = self.__bot.units(PYLON).closer_than(25, self.__bot.game_info.map_center)
                if not proxy.exists:
                    self.__request_proxy = True
        # proxy pylon
        if self.__request_proxy and self.__bot.can_afford(PYLON):
            self.__request_proxy = False
            p = self.__bot.game_info.map_center.towards(self.__bot.enemy_start_locations[0], 20)
            await self.__bot.build(PYLON, near=p)
        # distribuindo trabalhos para os soldados
        new_soldados = []
        for unit in self.__bot.military:
            found = False
            for soldado in self.__soldados:
                if unit.tag == soldado.tag:
                    new_soldados.append(soldado)
                    found = True
            if not found:
                soldado = Soldado(unit)
                new_soldados.append(soldado)
                if self.__defenders < self.__def_cost:
                    self.__defenders = self.__defenders + 1
                    soldado.role = Order.Defend
                else:
                    soldado.role = Order.Attack
        for unit in self.__bot.scout:
            found = False
            for soldado in self.__soldados:
                if unit.tag == soldado.tag:
                    new_soldados.append(soldado)
                    found = True
                    if soldado.target.distance_to(unit) < 5:
                        soldado.target = self.get_scout_location()
            if not found:
                soldado = Soldado(unit)
                new_soldados.append(soldado)
                soldado.role = Order.Scout
                soldado.order = Order.Scout
                soldado.target = self.get_scout_location()
        na = 0
        nd = 0
        for unit in self.__bot.observers:
            found = False
            for soldado in self.__soldados:
                if unit.tag == soldado.tag:
                    new_soldados.append(soldado)
                    found = True
                    if soldado.role == Order.Defend and self.__def_obs > 1 + self.__atk_obs:
                        soldado.role = Order.Attack
                        self.__def_obs = self.__def_obs - 1
                        self.__atk_obs = self.__atk_obs + 1
                    if soldado.role == Order.Attack and self.__def_obs + 1 <  self.__atk_obs:
                        soldado.role = Order.Defend
                        self.__def_obs = self.__def_obs - 1
                        self.__atk_obs = self.__atk_obs + 1
                    if soldado.role == Order.Attack:
                        na = na + 1
                    else:
                        nd = nd + 1
            if not found:
                soldado = Soldado(unit)
                new_soldados.append(soldado)
                if self.__atk_obs <= self.__def_obs:
                    soldado.role = Order.Attack
                    na = na + 1
                else:
                    soldado.role = Order.Defend
                    nd = nd + 1
        self.__def_obs = nd
        self.__atk_obs = na
        self.__soldados = new_soldados
        self.__defenders = 0
        self.__attackers = 0
        for soldado in self.__soldados:
            if soldado.role == Order.Defend and self.__defenders > self.__def_cost + 4:
                soldado.role = Order.Attack
            if soldado.role == Order.Attack and self.__defenders < self.__def_cost and self.__attackers > 15:
                soldado.role = Order.Defend
            if soldado.role == Order.Defend:
                self.__defenders = self.__defenders + 1
                soldado.order = Order.Defend
                soldado.target = self.__def_pos
            elif soldado.role == Order.Attack:
                self.__attackers = self.__attackers + 1
                if self.__atk_pos == None:
                    soldado.order = Order.Defend
                    soldado.target = self.__def_pos
                else:
                    soldado.order = Order.Attack
                    soldado.target = self.__cur_pos
        # run para soldados
        print(self.__defenders, ' defenders and ', self.__attackers, ' attackers')
        for unit in self.__bot.military | self.__bot.scout | self.__bot.observers:
            found = False
            for soldado in self.__soldados:
                if unit.tag == soldado.tag:
                    await soldado.run(iteration, unit, self.__bot)
                    found = True
        # temporary attack
        # attack
        #if self.__bot.units(STALKER).amount + 2 * self.__bot.units(IMMORTAL).amount > 20:
        #    for soldado in self.__soldados:
        #        if soldado.order == Order.Defend:
        #            soldado.order = Order.Attack
        #            soldado.target = self.select_target()
        #elif self.__bot.units(STALKER).amount > 6:
        #    for soldado in self.__soldados:
        #        if soldado.order == Order.Defend:
        #            soldado.target = self.__bot.game_info.map_center.towards(self.select_target(), 20)