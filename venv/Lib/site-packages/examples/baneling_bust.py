import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

class BanelingBustBot(sc2.BotAI):
    def __init__(self):
        self.moved_workers_to_gas = False

    async def on_step(self, state, iteration):
        if not self.units(HATCHERY).ready.exists:
            for unit in self.units.not_structure:
                await self.do(unit.attack(self.enemy_start_locations[0]))
            return

        hatchery = self.units(HATCHERY).ready.first
        larvae = self.units(LARVA)

        if iteration == 0:
            await self.do(self.units(OVERLORD).first.move(self.enemy_start_locations[0]))
            await self.do(larvae.random.train(DRONE))
            return

        elif larvae.exists:
            if self.supply_left <= 2 and not self.already_pending(OVERLORD):
                if self.can_afford(OVERLORD):
                    await self.do(larvae.random.train(OVERLORD))
            elif self.can_afford(DRONE) and self.workers.amount < 16:
                await self.do(larvae.random.train(DRONE))
            elif self.can_afford(ZERGLING):
                await self.do(larvae.random.train(ZERGLING))

        if not self.units(EXTRACTOR).exists and not self.already_pending(EXTRACTOR):
            if self.can_afford(EXTRACTOR):
                drone = self.workers.random
                target = state.vespene_geyser.closest_to(drone.position)
                await self.do(drone.build(EXTRACTOR, target))

        if self.units(EXTRACTOR).ready.exists and not self.moved_workers_to_gas:
            extractor = self.units(EXTRACTOR).first
            for drone in self.workers.prefer_idle.prefer_close_to(extractor).take(3):
                await self.do(drone.gather(extractor))
            self.moved_workers_to_gas = True

        if not self.units(SPAWNINGPOOL).exists and not self.already_pending(SPAWNINGPOOL):
            if self.can_afford(SPAWNINGPOOL):
                await self.build(SPAWNINGPOOL, near=hatchery)

        if not self.units(BANELINGNEST).exists and not self.already_pending(BANELINGNEST):
            if self.can_afford(BANELINGNEST):
                await self.build(BANELINGNEST, near=hatchery)

        if self.units(SPAWNINGPOOL).ready.exists:
            if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                await self.do(self.units(SPAWNINGPOOL).first(RESEARCH_ZERGLINGMETABOLICBOOST))

        if self.minerals > 500 and self.can_afford(HATCHERY):
            p = hatchery.position.to2.towards(self.game_info.map_center)
            await self.build(HATCHERY, p)

        if self.units(ZERGLING).exists and self.can_afford(BANELING):
            await self.do(self.units(ZERGLING).random.train(BANELING))

        army = self.units(ZERGLING) | self.units(BANELING)
        if iteration % 100 == 0:
            for unit in army:
                await self.do(unit.attack(self.enemy_start_locations[0]))

def main():
    sc2.run_game(sc2.maps.get("Newkirk Precinct TE"), [
        Bot(Race.Zerg, BanelingBustBot()),
        Computer(Race.Terran, Difficulty.VeryHard)
    ], realtime=False)

if __name__ == '__main__':
    main()
