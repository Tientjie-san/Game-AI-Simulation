from utils import calc_distance
import time

"""
Player plays an important role in the simulation, because we need to know the lvl and distance of the player in
certain states to determine what the next state of the mob should be. In the mob simulation we also needed to simulate
the player behaviour, because it is unrealistic to have a player idle all the time, for simulating the players
there are 2 options, one is to handle the player behaviour by ourself by providing input, the other is to hardcode
behaviour of the player. To keep it simple at every turn, the player moves 1 unit vector towards the mob.
"""


class Player:
    def __init__(self, lvl):
        self.hp = 100
        self.lvl = lvl
        self.position = [15, 15]

    def turn(self, mob):
        distance = calc_distance(self.position, mob.position)
        print(f"\nPlayer position: {int(self.position[0])} X, {int(self.position[1])} Y coordinates, mob position: "
              f"{int(mob.position[0])} X, {int(mob.position[1])} Y. distance: {distance} meters")
        # 1 stap van een speler is 1 meter, dus 1 meter richting mob
        time.sleep(1)
        dx, dy = (mob.position[0] - self.position[0], mob.position[1] - self.position[1])
        # unit vector van de directional vector
        udx, udy = (dx / distance, dy / distance)
        self.position[0] = self.position[0] + udx
        self.position[1] = self.position[1] + udy

    def respawn(self, mob):
        self.hp = 100
        self.lvl += 3
        self.position = [mob.position[0] + 10, mob.position[1] + 10]
