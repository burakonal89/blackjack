# -*- coding: utf-8 -*-

import numpy as np
from hand import Hand


class Player:
    """
    Player keeps money, a list of hand class, earnings and results.
    Player knows:
        strategy
        start money
        current hand
        other players hand
        dealers hand
    """

    def __init__(self,
                 type,
                 start_money,
                 id,
                 hands):
        self.type = type
        self.start_money = start_money
        self.id = id
        self.status = None
        self.hands = hands
        self.results = list()
        self.earnings = list()

    def apply_basic_strategy(self,
                             hand,
                             doubling_down=True):
        """
        Apply basic strategy rules given the player and the dealers hands.
        Details: http://www.cs.bu.edu/~hwxi/academic/courses/CS320/Spring02/assignments/06/basic-strategy.html
        :param hand: Hand class
        :param doubling_down:
        :return action: one of hit, double, stand, split actions.
        """
        dealer_card = self.hands[-1][0]
        if hand.hand[0] == hand.hand[1]:
            if doubling_down:
                if hand.hand[0] == 1:
                    return "split"
                elif hand.hand[0] == 2 or hand.hand[0] == 3:
                    if 2 <= dealer_card <= 7:
                        return "split"
                    else:
                        return "hit"
                elif hand.hand[0] == 4:
                    if 5 <= dealer_card <= 6:
                        return "split"
                    else:
                        return "hit"
                elif hand.hand[0] == 5:
                    if 2 <= dealer_card <= 9:
                        return "double"
                    else:
                        return "hit"
                elif hand.hand[0] == 6 or hand.hand[0] == 7:
                    if 2 <= dealer_card <= hand.hand[0]:
                        return "split"
                    else:
                        return "hit"
                elif hand.hand[0] == 8:
                    return "split"
                elif hand.hand[0] == 9:
                    if (2 <= dealer_card <= 6) or (8 <= dealer_card <= 9):
                        return "split"
                    else:
                        return "stand"
                elif hand.sum == 20:
                    return "stand"
            else:
                raise NotImplementedError("doubling down after splitting is allowed. otherwise not implemented")
        elif 1 not in hand.hand or len(hand.hand) > 2:
            if 5 <= hand.sum <= 8:
                return "hit"
            elif hand.sum == 9:
                if 3 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif hand.sum == 10:
                if 2 <= dealer_card <= 9:
                    return "double"
                else:
                    return "hit"
            elif hand.sum == 11:
                if dealer_card != 1:
                    return "double"
                else:
                    return "hit"
            elif hand.sum == 12:
                if 4 <= dealer_card <= 6:
                    return "stand"
                else:
                    return "hit"
            elif 13 <= hand.sum <= 16:
                if 4 <= dealer_card <= 6:
                    return "stand"
                else:
                    return "hit"
            elif 17 <= hand.sum:
                return "stand"
        elif 1 in hand.hand:
            if 13 <= hand.sum <= 14:
                if 5 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif 15 <= hand.sum <= 16:
                if 4 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif hand.sum == 17:
                if 3 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif hand.sum == 18:
                if 3 <= dealer_card <= 6:
                    return "double"
                elif dealer_card in [2, 7, 8]:
                    return "stand"
                else:
                    return "hit"
            elif 19 <= hand.sum <= 21:
                return "stand"
        return None

    def play(self, hand):
        """
        :param hand: a Hand class
        """
        if self.type == "basic":
            return self.apply_basic_strategy(hand)
        else:
            raise NotImplementedError("ILHAN!!!!!!!!!")

    # TODO: add card counting and pure random strategies.
