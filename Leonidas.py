import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import UnitTypeId as unitType
import random

PROBE = unitType.PROBE
NEXUS = unitType.NEXUS
PYLON = unitType.PYLON
ASSIMILATOR = unitType.ASSIMILATOR
GATEWAY = unitType.GATEWAY
CYBERNATICSCORE = unitType.CYBERNETICSCORE
STALKER = unitType.STALKER
ZEALOT = unitType.ZEALOT

class SpartaBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        #await self.expand()
        await self.build_offensive_buildings()
        await self.recruit_zealots()
        if self.units(ZEALOT).amount > 10:
            await self.build_offensive_force()
        await self.attack()

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE) and self.units(PROBE).amount < self.units(NEXUS).amount * 18:
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 3 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first)

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(25.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break;
                if not self.units(ASSIMILATOR).closer_than(1.0,vaspene):
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break;
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_offensive_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNATICSCORE):
                if self.can_afford(CYBERNATICSCORE) and not self.already_pending(CYBERNATICSCORE):
                    await self.build(CYBERNATICSCORE, near=pylon)

            elif len(self.units(GATEWAY)) < 3:
                    if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                        await self.build(GATEWAY,near=pylon)

    async def build_offensive_force(self):
        for gw in self.units(GATEWAY).ready:
            if self.can_afford(STALKER) and not self.already_pending(STALKER):
                await self.do(gw.train(STALKER))

    async def recruit_zealots(self):
        for gw in self.units(GATEWAY).ready:
            if self.can_afford(ZEALOT) and not self.already_pending(ZEALOT):
                await self.do(gw.train(ZEALOT))

    def find_target(self,state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        if self.units(STALKER).amount > 5 and self.units(ZEALOT).amount > 20:
            for s in self.units(STALKER).idle:
                await self.do(s.attack(self.find_target(self.state)))

        if self.units(STALKER).amount > 5:
            if len(self.known_enemy_units) > 0:
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))

run_game(maps.get("AbyssalReefLE"),
         [Bot(Race.Protoss, SpartaBot()),
          Computer(Race.Terran, Difficulty.Hard)], realtime=False)
