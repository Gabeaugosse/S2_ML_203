import default_params
from classes.agent import Agent
from strategies import *
import utils
from itertools import combinations
import random
import math

class Game() :
    def __init__(self, num_players: int, num_turns: int, strategy_mix: dict):
        """ strategy_mix : dict mapping Strategy -> proportion (float), must sum to 1.
        """
        self.num_players = num_players
        self.num_turns = num_turns

        self.logs = [] # History of all interactions among the game
        self.players = self._init_players(strategy_mix)
        self.players_indexes = list(self.players.keys())


    def _init_players(self, strategy_mix: dict) -> dict:
            """
            Instanciate agents depending on input proportion in the main file.
            """
            assert abs(sum(strategy_mix.values()) - 1.0) < 1e-6, "Proportion must sum to 1 !!"

            # Calcul des effectifs bruts
            raw_counts = {s: p * self.num_players for s, p in strategy_mix.items()}
            floor_counts = {s: math.floor(c) for s, c in raw_counts.items()}

            # Distribution du reste
            remainder = self.num_players - sum(floor_counts.values())
            sorted_by_remainder = sorted(strategy_mix.keys(),
                                        key=lambda s: raw_counts[s] - floor_counts[s],
                                        reverse=True)
            for i in range(remainder):
                floor_counts[sorted_by_remainder[i]] += 1

            # Instanciation des agents
            players = {}
            idx = 0
            for strategy, count in floor_counts.items():
                for _ in range(count):
                    players[idx] = Agent(idx, strategy)
                    idx += 1

            print("Start population :")
            for s, c in floor_counts.items():
                print(f"  {s.__name__:25s} : {c} agent(s) ({c/self.num_players:.1%})")

            return players


    def play(self) -> None:
        """ List every possible combination of players, and make them play NUM_TURNS times."""
        pairs = list(combinations(self.players_indexes, 2))
        random.shuffle(pairs)
        for p1, p2 in pairs:
            for _ in range(self.num_turns) :
                self.play_match(p1,p2)
    
    def play_match(self, p1_id: int, p2_id: int) -> None :
        """ Solve an interaction between two players."""
        # Instanciate each player into a variable
        player_1 = self.players[p1_id] 
        player_2 = self.players[p2_id]

        # Give the opponnent id to each player for them to choose their action
        first_player_action = player_1.choose_action(p2_id)
        second_player_action = player_2.choose_action(p1_id)
        # print(first_player_action, second_player_action)

        # Compute the outcome
        gains = default_params.GAIN_MATRIX[default_params.ACTIONS_INDEX[first_player_action]][default_params.ACTIONS_INDEX[second_player_action]]
        # print(gains)
        player_1_gain = gains[0]
        player_2_gain = gains[1]

        # print(player_1_gain,player_2_gain)
        
        # Update the logs and players history
        player_1.update_interactions(p2_id, {"player_action" : first_player_action, 
                                            "opponent_action" : second_player_action})
        player_2.update_interactions(p1_id, {"player_action" : second_player_action, 
                                            "opponent_action" : first_player_action})
            

        

    def random_matching(self) -> list :
        """ Takes every player initial id and shuffle it to do a perfect match shuffled list

        Returns:
            list: Shuffled list
        """
        return utils.shuffle(self.players_indexes.copy())
