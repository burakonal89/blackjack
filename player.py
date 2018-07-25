# -*- coding: utf-8 -*-
__author__ = "burakonal"

class Player:
    """
    Player keeps money, a list of hand class, earnings and results.
    """
    def __init__(self, money):
        self.type = None
        self.money = money
        self.results = list()
        self.earnings = list()
        self.hands = list()
