# -*- coding: utf-8 -*-
__author__ = "burakonal"
import numpy as np
from player import Player


class PlayerRandom(Player):
    """
    Player plays randomly in move.
    """

    def __init__(self, money):
        Player.__init__(self, money)
        Player.type = "random"

    @staticmethod
    def play(player_hand):
        actions = ["hit", "stand", "double"]
        if player_hand[0] == player_hand[1]:
            actions.append("split")
        return np.random.choice(actions)
