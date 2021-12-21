from utils import calc_distance
from clock import Clock

"""
Mob is the FSM we wanted to simulate in this project. the mob has an clock, which keeps track of the time the moment
when the mob is instantiated. The time is necessary to get out of the Idle, Victory and Defeat state.
The start state of the FSM is the Idle state, there is no end state. The simulation will end in 100 seconds
(in clock time of the mob, not real world) after the player has a higher lvl then the mob
"""

CMB_RANGE = 2
EVAL_RANGE = 5
MAX_IDLE = 60
LOS_RANGE = 15
THREE_SEC_INTERVAL = 3


class MobStateMachine:

    def __init__(self, hp, lvl, clock_speed=2):
        self.clock = Clock(clock_speed)
        self.clock.run()
        self.start_idle_time = self.clock.current_time
        self.hp = hp
        self.lvl = lvl
        self.victory_time = None
        self.start_state = "IDLE"
        self.end_state = None
        self.position = [0, 0]
        self.player_list = []

        self.states_transitions = {
            "IDLE": self.idle_transitions,
            "PLAYER_APPROACH": self.player_approach_transitions,
            "COMBAT": self.combat_transitions,
            "WALK": self.walk_transitions,
            "RESPAWN": self.respawn_transitions,
            "DEFEAT": self.defeat_transitions,
            "VICTORY": self.victory_transitions,
            "AGGRO": self.aggro_transitions,
            "EVAL": self.eval_transitions,
            "BACKONTRACK": self.bot_transitions,
            "REGEN": self.regen_transitions
        }
        self.current_state = self.start_state

    # First state: IDLE, function that transitions the idle state towards player_approach or walk depending on the
    # calculated distance between mob and player.
    def idle_transitions(self, player):
        self.current_state = "IDLE"
        self.summary(player)
        if self.player_in_range(player.position):
            return self.player_approach_transitions(player)
        if self.clock.current_time - self.start_idle_time < MAX_IDLE:
            return "IDLE"
        else:
            return self.walk_transitions(player)

    # Function that checks if the mob and player are within 15 meter distance.
    def player_in_range(self, player_pos):
        if calc_distance(self.position, player_pos) < LOS_RANGE:
            return True
        else:
            return False

    # Function state COMBAT, that will transition the current combat state to either a VICTORY or DEFEAT state.
    def combat_transitions(self, player):
        self.current_state = "COMBAT"
        self.summary(player)
        if self.lvl > player.lvl:
            self.victory_time = self.clock.current_time
            print("player got killed")
            player.respawn(self)
            return self.victory_transitions(player)
        else:
            self.hp = 0
            return self.defeat_transitions(player)

    # Function that transitions from the WALK state towards the player_approach state or staying within the WALK state.
    def walk_transitions(self, player):
        self.current_state = "WALK"
        self.summary(player)
        if player in self.player_list:
            # we didnt have time to make a nice walking route, so we decided moves 1 to the right
            self.position = [self.position[0]+1, 0]
            return "WALK"
        elif calc_distance(self.position, player.position) <= 15:
            return self.player_approach_transitions(player)
        else:
            return "WALK"

    # Respawn function that will restore the mob hitpoints and revert back into the IDLE state and x0, y0 coordinates.
    def respawn_transitions(self, player):
        self.current_state = "RESPAWN"
        self.summary(player)
        self.hp = 100
        self.position = [0, 0]
        return self.idle_transitions(player)

    # DEFEAT state function that will transition the current state into a RESPAWN state.
    def defeat_transitions(self, player):
        self.current_state = "DEFEAT"
        self.summary(player)
        return self.respawn_transitions(player)

    # REGEN state function that will transition the current state into a BoT state.
    def regen_transitions(self, player):
        self.current_state = "REGEN"
        self.summary(player)
        return self.bot_transitions(player)

    # VICTORY state function that will transition the current state into the REGEN state
    # if the 3 second interval condition has been met, if this isn't the case, repeat VICTORY state.
    def victory_transitions(self, player):
        self.current_state = "VICTORY"
        self.summary(player)
        if self.clock.current_time - self.victory_time >= THREE_SEC_INTERVAL:
            return self.regen_transitions(player)
        else:
            return "VICTORY"

    # AGGRO state function that will transition the current state into COMBAT state if the below 3 meters condition has
    # has been met, if this isn't the case, repeat AGGRO state.
    def aggro_transitions(self, player):
        self.current_state = "AGGRO"
        self.summary(player)
        if calc_distance(self.position, player.position) <= CMB_RANGE:
            return self.combat_transitions(player)
        else:
            self.move_towards_player(player)
            return "AGGRO"

    # EVALUATION state function, compares the mob level with the player level.
    # If the mob level exceeds the player, enter COMBAT state, if not return BoT state.
    def eval_transitions(self, player):
        self.current_state = "EVAL"
        self.summary(player)
        if self.lvl > player.lvl:
            return self.aggro_transitions(player)
        else:
            self.player_list.append(player)
            return self.walk_transitions(player)

    # BoT state function that will transition the current state into the WALK state.
    def bot_transitions(self, player):
        self.current_state = "BOT"
        self.summary(player)
        return self.walk_transitions(player)

    # PLAYER_APPROACH state function that calculates the distance between mob position and player position.
    # If the delta distance between mob and player <= 5 meters, enter EVAL state,
    # if the delta distance is bigger than 15 m enter BoT state.
    # Should the above mentioned conditions not be met, return the move_towards_player function.
    def player_approach_transitions(self, player):
        self.current_state = "PLAYER_APPROACH"
        self.summary(player)
        distance = calc_distance(self.position, player.position)
        if distance > LOS_RANGE:
            return self.bot_transitions(player)
        elif distance <= EVAL_RANGE:
            return self.eval_transitions(player)
        else:
            self.move_towards_player(player)

        # Secondary statement that will immediately evaluate the player
        # if the distance between mob and player is equal or below 5 meters,
        # in case of player movement that will interrupt the evaluation process.
        new_distance = calc_distance(self.position, player.position)
        if new_distance <= EVAL_RANGE:
            return self.eval_transitions(player)
        else:
            return "PLAYER_APPROACH"

    # Function that uses the calculated distance between mob and player in order to close the distance between these two
    # classes. The x and y coordinates of both mob and player will be subtracted of each other.
    # The result is a float that will multiply itself by 0.9 (a value that represents the 'lower' speed compared to the
    # 1.0 of the player.) and then add itself to the current X and Y coordinate values.
    def move_towards_player(self, player):
        distance = calc_distance(self.position, player.position)
        dx, dy = (player.position[0] - self.position[0], player.position[1] - self.position[1])
        # unit vector of the directional vector
        udx, udy = (dx / distance, dy / distance)
        self.position[0] = self.position[0] + 0.9 * udx
        self.position[1] = self.position[1] + 0.9 * udy

    def summary(self, player):
        print(f"start_distance = {calc_distance(self.position, player.position)}")
        print(f"mob_lvl = {self.lvl}")
        print(f"player_lvl = {player.lvl}")
        print(f"current_state: {self.current_state}")
        print(f"clock {self.clock.current_time}")
