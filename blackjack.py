# -*- coding: utf-8 -*-
__author__ = "burakonal"
import numpy as np
import logging

class Player:

    def __init__(self, money, bet):
        self.money = money
        self.bet = bet
        self.result = list()
        self.earnings = list()
        self.player_hand = None

    def apply_basic_strategy(self, player, dealer, doubling_down=True):
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

class Game:

    def __init__(self, player_num, money, bet, deck_num, logging_level):

        # logging
        numeric_level = getattr(logging, logging_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: {}'.format(logging_level))
        logFormatter = logging.Formatter('%(levelname)s:%(message)s')
        self.logger = logging.getLogger('logger')
        self.logger.setLevel(level=numeric_level)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        self.logger.addHandler(consoleHandler)

        self.i = 0
        self.round = 0
        self.player_num = player_num

        self.bet = bet
        self.deck = np.repeat(np.arange(1,14), 4 * deck_num)
        np.random.shuffle(self.deck)  # inline shuffle
        self.ratios = {"blackjack": 1.5, "win": 1, "push": 0, "lost": -1, "insurance": np.NaN}  # ratios
        self.logger.info("Deck: {}".format(self.deck))
        self.cut_card = np.random.randint(low=int(len(self.deck) / 2), high=int(len(self.deck)))
        self.logger.info("Deck length: {}".format(len(self.deck)))
        self.logger.info("Cut card: {}".format(self.cut_card))
        self.players = list()
        for i in range(player_num):
            self.players.append(Player(money, bet))

    def ceil_to_10(self):
        func = lambda x: 10 if x > 10 else x
        return np.vectorize(func)

    def calculate_round(self, ratio, bet):
        earning = bet * ratio
        self.money = self.money + earning + np.sign(ratio + 1) * bet
        return earning

    # def play_round(self, round_, action, deck, player, dealer, bet, money):
    #     """
    #     Play one round of the game.
    #     :param round_: current round of the game
    #     :param action: action of the player. One of double, split, hit, stand.
    #     :param i: index of the deck
    #     :param cut_card: cut_card of the deck (where the game stops and a new one begins after shuffling)
    #     :param deck:
    #     :param bet: current bet of the player
    #     :money: current money of the player
    #     :return: i, cut_card, player, dealer, money
    #     """
    #     if action == "stand":
    #         dealer_sum = np.sum(dealer)
    #         player_sum = np.sum(player)
    #         if player_sum == 21:
    #             if dealer_sum == 21:
    #                 ratio = self.ratios["push"]
    #                 earning = self.calculate_round(ratio)
    #                 self.logger.debug("Round:{} Push! Player:{} Dealer:{} Current bet:{} Earning ratio:{} Earning:{} Current Money:{}".format(round_, player, dealer, bet, ratio, earning, self.money))
    #             else:
    #                 ratio = self.ratios["blackjack"]
    #                 earning = self.calculate_round(ratio)
    #                 self.logger.debug("Round:{} Player BlackJack! Player:{} Dealer:{}, Current bet:{} Earning ratio:{} Earning:{} Current Money:{}".format(round_, player, dealer, bet, ratio, earning, self.money))
    #         else:
    #             while dealer_sum < 17:
    #                 # win case
    #                 if dealer_sum > 21 or (21 - dealer_sum) > (21 - player_sum):
    #                     ratio = ratios["win"]
    #                     earning = calculate_round(ratio)
    #                     logger.debug("Round:{} Win! Player:{} Dealer:{}, Current bet:{} Earning ratio:{} Earning:{} Current Money:{}".format(round_, player, dealer, bet, ratio, earning, self.money))
    #                 # lost case
    #                 if dealer_sum == 21 or (21 - dealer_sum) < (21 - player_sum):
    #                     ratio = ratios["lost"]
    #                     earning = calculate_round(ratio)
    #                     logger.debug("Round:{} Lost! Player:{} Dealer:{}, Current bet:{} Earning ratio:{} Earning:{} Current Money:{}".format(round_, player, dealer, bet, ratio, earning, self.money))
    #                 dealer = np.append(dealer, self.ceil_to_10(self.deck[i]))
    #                 self.i += 1
    #                 self.cut_card -= 1
    #                 dealer_sum = np.sum(dealer)
    #     elif action == "hit":
    #         player = np.append(player, self.ceil_to_10(deck[i]))
    #         self.i += 1
    #         self.cut_card -= 1
    #         player_sum = np.sum(player)
    #         # busted case
    #         if player_sum > 21:
    #             ratio = ratios["lost"]
    #             earning = calculate_round(ratio)
    #             logger.debug("Round:{} Lost! Player:{} Dealer:{}, Current bet:{} Earning ratio:{} Earning:{} Current Money:{}".format(round_, player, dealer, bet, ratio, earning, self.money))
    #         else:
    #             action = self.apply_basic_strategy(player, dealer)
    #             play_round()

    def play_game(self):


        while self.cut_card > self.i and self.i < len(self.deck):
            self.i += 1 #burning the first card.
            self.round += 1
            for i in range(self.player_num):
                self.players[i].bet = self.bet
                self.players[i].money -= self.bet
                self.players[i].player_hand = self.deck[[self.i+i, self.i + self.player_num+1+i]]
            self.dealer_hand = self.deck[[self.i + self.player_num, self.i + 2*self.player_num+1]]
            self.i += (self.player_num+1)*2
            for i in range(self.player_num):
                self.logger.debug("Round: {} Player-{} hand: {}".format(self.round, i, self.players[i].player_hand))
            self.logger.debug("Round: {} Dealer hand: {}".format(self.round, self.dealer_hand))

game = Game(4, 100, 1, 4, "debug")
game.play_game()