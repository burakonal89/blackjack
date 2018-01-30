# -*- coding: utf-8 -*-
__author__ = "burakonal"


class Hand:
    """
    Hand class keeps list of hands, bets and status.
    """
    def __init__(self):
        self.hand = None
        self.bet = None
        self.status = None
        self.sum = None