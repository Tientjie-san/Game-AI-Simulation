from mob import MobStateMachine
from player import Player
import random


# Simulation function that acts as the start function for the whole process.
def simulate(mob, player):
    state_transition = mob.states_transitions[mob.current_state]
    while True:
        player.turn(mob)
        mob.current_state = state_transition(player)
        state_transition = mob.states_transitions[mob.current_state]
        if mob.victory_time is not None: 
            if mob.clock.current_time - mob.victory_time >= 100:
                print("times up!")
                mob.clock.stop()
                break


simulate(MobStateMachine(hp=100, lvl=100, clock_speed=2), Player(lvl=random.randint(70, 90)))
