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
        self.hand = None

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
    # TODO: add card counting and pure random strategies.


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
        # TODO: add type of players as well (for instance, basic strategy, random or (if you can) card counting.
        self.player_num = player_num

        self.bet = bet
        self.deck = np.repeat(np.arange(1, 14), 4 * deck_num)
        self.deck_length = len(self.deck)
        self.dealer_hand = None
        # inline shuffle
        np.random.shuffle(self.deck)
        # ratios. Subject to change.
        self.ratios = {"blackjack": 1.5, "win": 1, "push": 0, "lost": -1, "insurance": np.NaN}
        self.logger.info("Deck: {}".format(self.deck))
        # make sure cut card put in the second half of the cards.
        self.cut_card = np.random.randint(low=int(self.deck_length / 2), high=int(self.deck_length))
        self.logger.info("Deck length: {}".format(len(self.deck)))
        self.logger.info("Cut card: {}".format(self.cut_card))
        self.players = list()
        for i in range(player_num):
            self.players.append(Player(money, bet))

        self.ceil_to_10 = np.vectorize(self.ceil_2_10)

    @staticmethod
    def ceil_2_10(num):
        """
        Cap the value of the card to 10.
        :param num:
        :return:
        """

        if num > 10:
            return 10
        return num

    def calculate_round(self, ratio, player):
        earning = player.bet * ratio
        player.money = player.money + max(0, earning) + np.sign(ratio + 1) * player.bet
        return earning

    def dealer_sum(self):

        # TODO: complete
        return self.dealer_hand.sum()

    def play_round(self, round_, action, player):
        """
        Play one round of the game.
        :param round_: current round of the game
        :param action: action of the hand. One of double, split, hit, stand.
        :param i: index of the deck
        :param cut_card: cut_card of the deck (where the game stops and a new one begins after shuffling)
        :param deck:
        :param bet: current bet of the hand
        :money: current money of the hand
        :return: Nothing, updates player, dealer and game index.
        """
        if action == "stand":
            # TODO: Dealer sum should be defined. Ace can worht 1 or 11 depending on the combination.
            dealer_sum = np.sum(self.dealer_hand)
            player_sum = np.sum(player.hand)
            # TODO blackjack happens iff card number is 2 and sum is 21. otherwise its simple 21.
            if player_sum == 21:
                if dealer_sum == 21:
                    ratio = self.ratios["push"]
                    earning = self.calculate_round(ratio, player)
                    self.logger.debug("Round: {} Push! Player hand:{} Dealer hand:{} Current bet:{} Earning ratio:{} "
                                      "Earning:{} Current Money:{}".format(round_, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))
                else:
                    ratio = self.ratios["blackjack"]
                    earning = self.calculate_round(ratio, player)
                    self.logger.debug("Round: {} BlackJack! Player hand:{} Dealer hand:{} Current bet:{} Earning ratio:{} "
                                      "Earning:{} Current Money:{}".format(round_, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))
            else:
                while dealer_sum < 17:
                    # draw one more time
                    self.dealer_hand = np.append(self.dealer_hand, self.ceil_to_10(self.deck[self.i]))
                    self.i += 1
                    self.cut_card -= 1
                    dealer_sum = np.sum(self.dealer_hand)
                # win case
                if dealer_sum > 21 or (21 - dealer_sum) > (21 - player_sum):
                    ratio = self.ratios["win"]
                    earning = self.calculate_round(ratio, player)
                    self.logger.debug("Round: {} Win! Player hand:{} Dealer hand:{} Current bet:{} Earning ratio:{}"
                                      "Earning:{} Current Money:{}".format(round_, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))
                # lost case
                elif dealer_sum == 21 or (21 - dealer_sum) < (21 - player_sum):
                    ratio = self.ratios["lost"]
                    earning = self.calculate_round(ratio, player)
                    self.logger.debug("Round: {} Lost! Player hand:{} Dealer hand:{} Current bet:{} Earning ratio:{}"
                                      "Earning:{} Current Money:{}".format(round_, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))
                    return
        elif action == "hit":
            player.hand = np.append(player.hand, self.ceil_to_10(self.deck[self.i]))
            self.i += 1
            self.cut_card -= 1
            player_sum = np.sum(player.hand)
            # busted case
            if player_sum > 21:
                ratio = self.ratios["lost"]
                earning = self.calculate_round(ratio, player)
                self.logger.debug("Round: {} Lost! Player hand:{} Dealer hand:{} Current bet:{} Earning ratio:{} "
                                  "Earning:{} Current Money:{}".format(round_, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))
            # if not busted, the function will be recalled.
            else:
                action = player.apply_basic_strategy(player.hand, self.dealer_hand)
                self.play_round(round_, action, player.hand)

    def play_game(self):


        while self.cut_card > self.i and self.i < len(self.deck):
            # self.i += 1  # burning the first card.
            self.round += 1
            for i in range(self.player_num):
                # TODO: each player can set up a new bet for each round. Currently playing with the minimum bet.
                self.players[i].bet = self.bet
                self.players[i].money -= self.bet
                self.players[i].hand = self.ceil_to_10(self.deck[[self.i+i, self.i+self.player_num+1+i]])
            self.dealer_hand = self.deck[[self.i+self.player_num, self.i+2*self.player_num+1]]
            self.i += (self.player_num+1)*2
            for i in range(self.player_num):
                self.logger.debug("Round: {} Player-{} hand: {}".format(self.round, i, self.players[i].hand))
            self.logger.debug("Round: {} Dealer hand: {}".format(self.round, self.dealer_hand))


game = Game(3, 100, 1, 4, "debug")
game.play_game()