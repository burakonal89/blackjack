# -*- coding: utf-8 -*-
__author__ = "burakonal"
import numpy as np
import logging

class Player:

    def __init__(self, money):
        self.money = money

    def apply_basic_strategy(player, dealer, doubling_down=True):
        """
        Apply basic strategy rules given player and dealer hands.
        Details: http://www.cs.bu.edu/~hwxi/academic/courses/CS320/Spring02/assignments/06/basic-strategy.html
        :param player: player hand ceiled to 10
        :param dealer: dealer hand ceiled to 10
        :return action: one of hit, double, stand, split actions.
        """
        summe = sum(player)
        if player[0] != player[1]:
            if 1 not in player:
                if summe <= 8:
                    return "hit"
                elif summe == 9:
                    if dealer >= 3 and dealer <= 6:
                        return "double"
                    return "hit"
                elif summe == 10:
                    if dealer >= 2 and dealer <= 9:
                        return "double"
                    return "hit"
                elif summe == 11:
                    if dealer >= 2 and dealer <= 10:
                        return "double"
                    return "hit"
                elif summe == 12:
                    if dealer >= 4 and dealer <= 6:
                        return "stand"
                    return "hit"
                elif summe >= 13 and summe <= 16:
                    if dealer >= 2 and dealer <= 6:
                        return "stand"
                    return "hit"
                return "stand"
            else:
                if summe == 3 or summe == 4:
                    if dealer == 5 or dealer == 6:
                        return "double"
                    return "hit"
                elif summe == 5 or summe == 6:
                    if dealer >= 4 and dealer <= 6:
                        return "double"
                    return "hit"
                elif summe == 7:
                    if dealer >= 3 and dealer <= 6:
                        return "double"
                    return "hit"
                elif summe == 8:
                    if dealer >= 3 and dealer <= 6:
                        return "double"
                    elif dealer == 2 or dealer == 7 or dealer == 8:
                        return "stand"
                    return "hit"
                else:
                    return "stand"
        else:
            if doubling_down:
                if player[0] == 1:
                    return "split"
                elif player[0] == 2 or player[0] == 3:
                    if dealer >= 2 and dealer <= 7:
                        return "split"
                    return "hit"
                elif player[0] == 4:
                    if dealer == 5 or dealer == 6:
                        return "split"
                    return "hit"
                elif player[0] == 5:
                    if dealer >= 2 and dealer <= 9:
                        return "double"
                    return "hit"
                elif player[0] == 6 or player[0] == 7:
                    if dealer >= 2 and dealer <= player[0]:
                        return "split"
                    return "hit"
                elif player[0] == 8:
                    return "split"
                elif player[0] == 9:
                    if dealer == 1 or dealer == 7 or dealer == 10:
                        return "stand"
                    return "split"
                return "stand"
            else:
                if player[0] == 2 or player[0] == 3:
                    if dealer >= 4 and dealer <= 7:
                        return "split"
                    return "hit"
                elif player[0] == 4:
                    return "hit"
                elif player[0] == 6:
                    if dealer >= 3 and dealer <= 6:
                        return "split"
                    return "hit"