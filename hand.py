# -*- coding: utf-8 -*-
__author__ = "burakonal"


class Hand:
    """
    Hand class keeps list of hands, bets and status.
    """
    def __init__(self, bet):
        self.hand = None
        self.bet = bet
        self.status = None
        self.sum = None
