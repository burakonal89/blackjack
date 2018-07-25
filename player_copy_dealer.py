# -*- coding: utf-8 -*-
__author__ = "burakonal"
from player import Player


class PlayerCopyDealer(Player):

    def __init__(self, money):
        Player.__init__(self, money)
        self.type = "copy dealer"

    @staticmethod
    def play(player_hand_sum):
        if player_hand_sum >=17:
            return "stand"
        else:
            return "hit"
