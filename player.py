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

    @staticmethod
    def calculate_hand_sum(hand):
        """

        """
        sum_1 = sum(min(10, card) for card in hand)
        if 1 in hand:
            hand_2 = hand.copy()
            hand_2[hand_2.index(1)] = 11
            sum_2 = sum(min(10, card) for card in hand_2)
        else:
            sum_2 = sum_1
        if abs(21-sum_1) < abs(21-sum_2) and sum_1 < sum_2:
            return sum_1
        return sum_2

    def apply_basic_strategy(self,
                             hand,
                             doubling_down=True):
        """
        Apply basic strategy rules given the player and the dealers hands.
        Details: http://www.cs.bu.edu/~hwxi/academic/courses/CS320/Spring02/assignments/06/basic-strategy.html
        :param hand:
        :param doubling_down:
        :return action: one of hit, double, stand, split actions.
        """
        hand_sum = Player.calculate_hand_sum(hand)
        dealer_card = self.hands[-1][0]
        if hand[0] == hand[1]:
            if doubling_down:
                if hand[0] == 1:
                    return "split"
                elif hand[0] == 2 or hand[0] == 3:
                    if 2 <= dealer_card <= 7:
                        return "split"
                    else:
                        return "hit"
                elif hand[0] == 4:
                    if 5 <= dealer_card <= 6:
                        return "split"
                    else:
                        return "hit"
                elif hand[0] == 5:
                    if 2 <= dealer_card <= 9:
                        return "double"
                    else:
                        return "hit"
                elif hand[0] == 6 or hand[0] == 7:
                    if 2 <= dealer_card <= hand[0]:
                        return "split"
                    else:
                        return "hit"
                elif hand[0] == 8:
                    return "split"
                elif hand[0] == 9:
                    if (2 <= dealer_card <= 6) or (8 <= dealer_card <= 9):
                        return "split"
                    else:
                        return "stand"
                elif hand_sum == 20:
                    return "stand"
            else:
                raise NotImplementedError("doubling down after splitting is allowed. otherwise not implemented")
        elif 1 not in hand:
            if 5 <= hand_sum <= 8:
                return "hit"
            elif hand_sum == 9:
                if 3 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif hand_sum == 10:
                if 2 <= dealer_card <= 9:
                    return "double"
                else:
                    return "hit"
            elif hand_sum == 11:
                if dealer_card != 1:
                    return "double"
                else:
                    return "hit"
            elif hand_sum == 12:
                if 4 <= dealer_card <= 6:
                    return "stand"
                else:
                    return "hit"
            elif 13 <= hand_sum <= 16:
                if 4 <= dealer_card <= 6:
                    return "stand"
                else:
                    return "hit"
            elif 17 <= hand_sum:
                return "stand"
        elif 1 in hand:
            if 3 <= hand_sum <= 4:
                if 5 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif 5 <= hand_sum <= 6:
                if 4 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif hand_sum == 7:
                if 3 <= dealer_card <= 6:
                    return "double"
                else:
                    return "hit"
            elif hand_sum == 8:
                if 3 <= dealer_card <= 6:
                    return "double"
                elif dealer_card in [2, 7, 8]:
                    return "stand"
                else:
                    return "hit"
            elif 9 <= dealer_card <= 11:
                return "stand"
        return None

    def play(self, hand):
        """
        :param hand: a Hand class
        """
        if self.type == "basic":
            return self.apply_basic_strategy(hand.hand)
        else:
            raise NotImplementedError("ILHAN!!!!!!!!!")

    # TODO: add card counting and pure random strategies.
