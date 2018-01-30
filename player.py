# -*- coding: utf-8 -*-
__author__ = "burakonal"

import numpy as np
from hand import Hand
class Player:
    """
    Player keeps money, a list of hand class, earnings and results.
    """
    def __init__(self, money):
        self.money = money
        self.results = list()
        self.earnings = list()
        self.hands = list()

    @staticmethod
    def apply_basic_strategy(player_hand, dealer_hand, doubling_down=True):
        """
        Apply basic strategy rules given player and dealer hands.
        Details: http://www.cs.bu.edu/~hwxi/academic/courses/CS320/Spring02/assignments/06/basic-strategy.html
        :param player_hand: player hand ceiled to 10
        :param dealer_hand: dealer hand ceiled to 10
        :return action: one of hit, double, stand, split actions.
        """

        player_sum = player_hand.sum()
        if 1 in player_hand:
            # remove the ace.
            player_hand = np.delete(player_hand, np.argmax(player_hand == 1))
            player_sum = player_hand.sum()
            if player_sum > 10:
                flag = True
                player_hand = np.append(player_hand, [1])
                player_sum = player_hand.sum()
            else:
                flag = False
                player_hand = np.append(player_hand, [1])
        else:
            flag = True
        if player_hand[0] != player_hand[1]:
            if flag:
                if player_sum <= 8:
                    return "hit"
                elif player_sum == 9:
                    if dealer_hand >= 3 and dealer_hand <= 6:
                        return "double"
                    return "hit"
                elif player_sum == 10:
                    if dealer_hand >= 2 and dealer_hand <= 9:
                        return "double"
                    return "hit"
                elif player_sum == 11:
                    if dealer_hand >= 2 and dealer_hand <= 10:
                        return "double"
                    return "hit"
                elif player_sum == 12:
                    if dealer_hand >= 4 and dealer_hand <= 6:
                        return "stand"
                    return "hit"
                elif player_sum >= 13 and player_sum <= 16:
                    if dealer_hand >= 2 and dealer_hand <= 6:
                        return "stand"
                    else:
                        return "hit"
                else:
                    return "stand"
            else:
                if player_sum == 3 or player_sum == 4:
                    if dealer_hand == 5 or dealer_hand == 6:
                        return "double"
                    return "hit"
                elif player_sum == 5 or player_sum == 6:
                    if dealer_hand >= 4 and dealer_hand <= 6:
                        return "double"
                    return "hit"
                elif player_sum == 7:
                    if dealer_hand >= 3 and dealer_hand <= 6:
                        return "double"
                    return "hit"
                elif player_sum == 8:
                    if dealer_hand >= 3 and dealer_hand <= 6:
                        return "double"
                    elif dealer_hand == 2 or dealer_hand == 7 or dealer_hand == 8:
                        return "stand"
                    return "hit"
                else:
                    return "stand"
        else:
            if doubling_down:
                if player_hand[0] == 1:
                    return "split"
                elif player_hand[0] == 2 or player_hand[0] == 3:
                    if dealer_hand >= 2 and dealer_hand <= 7:
                        return "split"
                    return "hit"
                elif player_hand[0] == 4:
                    if dealer_hand == 5 or dealer_hand == 6:
                        return "split"
                    return "hit"
                elif player_hand[0] == 5:
                    if dealer_hand >= 2 and dealer_hand <= 9:
                        return "double"
                    return "hit"
                elif player_hand[0] == 6 or player_hand[0] == 7:
                    if dealer_hand >= 2 and dealer_hand <= player_hand[0]:
                        return "split"
                    return "hit"
                elif player_hand[0] == 8:
                    return "split"
                elif player_hand[0] == 9:
                    if dealer_hand == 1 or dealer_hand == 7 or dealer_hand == 10:
                        return "stand"
                    return "split"
                return "stand"
            else:
                if player_hand[0] == 2 or player_hand[0] == 3:
                    if dealer_hand >= 4 and dealer_hand <= 7:
                        return "split"
                    return "hit"
                elif player_hand[0] == 4:
                    return "hit"
                elif player_hand[0] == 6:
                    if dealer_hand >= 3 and dealer_hand <= 6:
                        return "split"
                    return "hit"

    # TODO: add card counting and pure random strategies.