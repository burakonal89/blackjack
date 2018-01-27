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
        self.status = None

    def apply_basic_strategy(self, player_hand, dealer_hand, doubling_down=True):
        """
        Apply basic strategy rules given player and dealer hands.
        Details: http://www.cs.bu.edu/~hwxi/academic/courses/CS320/Spring02/assignments/06/basic-strategy.html
        :param player_hand: player hand ceiled to 10
        :param dealer_hand: dealer hand ceiled to 10
        :return action: one of hit, double, stand, split actions.
        """
        player_sum = player_hand.sum()
        if player_hand[0] != player_hand[1]:
            if 1 not in player_hand:
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
                    return "hit"
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


class Game:

    def __init__(self, player_num, start_money, bet, deck_num, logging_level, dealer_threshold=17):

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

        self.index = 0
        self.round = 0
        # TODO: add type of players as well (for instance, basic strategy, random or (if you can) card counting.
        self.player_num = player_num

        self.bet = bet
        self.deck = np.repeat(np.arange(1, 14), 4 * deck_num)
        self.deck_length = len(self.deck)
        self.dealer_hand = None
        self.dealer_threshold = dealer_threshold
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
            self.players.append(Player(start_money, bet))

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
    @staticmethod
    def is_blackjack(hand):
        """
        Checks whether given hand is black jack.
        :param hand:
        :return:
        """
        if len(hand) == 2 and 1 in hand and 10 in hand:
            return True
        return False

    @staticmethod
    def hand_sum(hand):
        """
        Ace can worth 1 or 11 depending on the hand.
        :param hand: List of cards from players or the dealer
        :return: closest sum to 21
        """
        prev_sum = hand.sum()
        curr_sum = prev_sum
        if 1 in hand:
            hand[np.where(hand == 1)[0][0]] = 11
            curr_sum = hand.sum()
        if abs(21-curr_sum) < abs(21-prev_sum) and curr_sum < 21:
            return curr_sum
        return prev_sum

    def finish_round(self, player):
        """
        :param player:
        :return:
        """
        player_sum = self.hand_sum(player.hand.copy())
        dealer_sum = self.hand_sum(self.dealer_hand.copy())
        # win case
        if dealer_sum > 21 or 21 - dealer_sum > 21 - player_sum:
            ratio = self.ratios["win"]
            earning = self.calculate_round(ratio, player)
            self.logger.debug("Round:{}\tWin!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                              "Earning:{}\tCurrent Money:{}".format(self.round, player.hand, self.dealer_hand,
                                                                   player.bet, ratio, earning, player.money))
        # lost case
        elif 21 - dealer_sum < 21 - player_sum:
            ratio = self.ratios["lost"]
            earning = self.calculate_round(ratio, player)
            self.logger.debug("Round:{}\tLost!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                              "Earning:{}\tCurrent Money:{}".format(self.round, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))
        else:
            ratio = self.ratios["push"]
            earning = self.calculate_round(ratio, player)
            self.logger.debug("Round:{}\tPush!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                              "Earning:{}\tCurrent Money:{}".format(self.round, player.hand, self.dealer_hand, player.bet, ratio, earning, player.money))

    def play_round_dealer(self):
        """
        Play one round for the dealer.
        :return:
        """
        dealer_sum = self.hand_sum(self.dealer_hand.copy())
        while dealer_sum < self.dealer_threshold:
            self.dealer_hand = np.append(self.dealer_hand, self.ceil_to_10(self.deck[self.index]))
            if self.index > self.deck_length:
                self.logger.debug("Round: {}\t Current index: {}\t. Game ends.".format(self.round, self.index))
                return False
            self.index += 1
            self.logger.debug("Round:{}\tDealer hits.\tDealer hand:{}".format(self.round, self.dealer_hand))
            dealer_sum = self.hand_sum(self.dealer_hand.copy())
        return True
    def play_round_player(self, action, player):
        """
        Play one round of the game for a player.
        :param action: action of the hand. One of double, split, hit, stand.
        :param player:
        :return: Nothing, updates player, dealer and game index.
        """
        if action == "stand":
            self.logger.debug("Round:{}\tPlayer stands.\tPlayer hand:{}\tDealer hand:{}".format(self.round, player.hand,
                                                                                                self.dealer_hand))
            return True
        elif action == "hit":
            if self.index > self.deck_length:
                self.logger.debug("Round: {}\t Current index: {}\t. Game ends.".format(self.round, self.index))
                return False
            player.hand = np.append(player.hand, self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            self.logger.debug("Round:{}\tPlayer hits.\tPlayer hand:{}\tDealer hand:{}".format(self.round, player.hand,
                                                                                              self.dealer_hand))
            player_sum = self.hand_sum(player.hand.copy())
            # busted
            if player_sum > 21:
                ratio = self.ratios["lost"]
                earning = self.calculate_round(ratio, player)
                self.logger.debug("Round:{}\tLost!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, player.hand, self.dealer_hand,
                                                                        player.bet, ratio, earning, player.money))
                player.status = "lost"
                return True
            else:
                action = player.apply_basic_strategy(player.hand, self.dealer_hand[0])
                return self.play_round_player(action, player)
        elif action == "split":
            self.logger.debug("Round:{}\tPlayer splits.\tPlayer hand:{}\tDealer hand:{}".format(self.round, player.hand,
                                                                                               self.dealer_hand))

            if self.index+2 > self.deck_length:
                self.logger.debug("Round: {}\t Current index: {}\t. Game ends.".format(self.round, self.index))
                return False
            player_hand = player.hand
            player_bet = player.bet
            first = np.append(player_hand[0], self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            player.hand = first
            action = player.apply_basic_strategy(player.hand, self.dealer_hand[0])
            self.play_round_player(action, player)
            player.bet = player_bet
            second = np.append(player_hand[1], self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            player.hand = second
            action = player.apply_basic_strategy(player.hand, self.dealer_hand[0])
            return self.play_round_player(action, player)
        elif action == "double":
            if self.index > self.deck_length:
                self.logger.debug("Round: {}\t Current index: {}\t. Game ends.".format(self.round, self.index))
                return False
            player.money -= player.bet
            player.bet = 2 * player.bet
            player.hand = np.append(player.hand, self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            self.logger.debug("Round:{}\tPlayer doubles.\tPlayer hand:{}\tDealer hand:{}".format(self.round, player.hand,
                                                                                                 self.dealer_hand))
            player_sum = self.hand_sum(player.hand.copy())
            # busted
            if player_sum > 21:
                ratio = self.ratios["lost"]
                earning = self.calculate_round(ratio, player)
                self.logger.debug("Round:{}\tLost!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, player.hand, self.dealer_hand,
                                                                       player.bet, ratio, earning, player.money))
                player.status = "lost"
            return True

    def play_round(self):
        """
        Play one round of the game for each player and finally for the dealer.

        :return: updated card index, player money.
        """

        # check if enough cards available.
        if self.index + 2 * self.player_num + 1 > self.deck_length:
            self.logger.debug("Round: {}\t Current index is: {}. Cards cannot be distributed. The game finishes. "
                              "The index is set to deck length.".format(self.round, self.index))
            self.index = self.deck_length
            return False
        for i in range(self.player_num):
            # TODO: each player can set up a new bet for each round. Currently playing with the minimum bet.
            self.players[i].bet = self.bet
            self.players[i].money -= self.bet
            self.players[i].hand = self.ceil_to_10(self.deck[[self.index + i, self.index + self.player_num + 1 + i]])
            self.players[i].status = None
        self.dealer_hand = self.ceil_to_10(self.deck[[self.index + self.player_num, self.index + 2 * self.player_num + 1]])
        self.index += (self.player_num + 1) * 2
        for i in range(self.player_num):
            self.logger.debug("Round:{}\tPlayer-{} hand:{}".format(self.round, i, self.players[i].hand))
        self.logger.debug("Round:{}\tDealer hand:{}".format(self.round, self.dealer_hand))

        # play game for each player
        for i in range(self.player_num):
            # player got black jack
            if self.is_blackjack(self.players[i].hand):
                # dealer got black jack
                if self.is_blackjack(self.dealer_hand):
                    ratio = self.ratios["push"]
                    earning = self.calculate_round(ratio, self.players[i])
                    self.logger.debug("Round:{}\tPush!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\t"
                                      "Earning ratio:{}\tEarning:{}\tCurrent Money:{}".format(self.round,
                                                                                              self.players[i].hand,
                                                                                              self.dealer_hand,
                                                                                              self.players[i].bet,
                                                                                              ratio, earning,
                                                                                              self.players[i].money))
                else:
                    ratio = self.ratios["blackjack"]
                    earning = self.calculate_round(ratio, self.players[i])
                    self.logger.debug("Round:{}\tBlack Jack!\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\t"
                                      "Earning ratio:{}\tEarning:{}\tCurrent Money:{}".format(self.round,
                                                                                              self.players[i].hand,
                                                                                              self.dealer_hand,
                                                                                              self.players[i].bet,
                                                                                              ratio, earning,
                                                                                              self.players[i].money))
                return True
            # dealer got black jack
            elif self.is_blackjack(self.dealer_hand):
                ratio = self.ratios["lost"]
                earning = self.calculate_round(ratio, self.players[i])
                self.logger.debug("Round:{} Lost!\tPlayer hand:{} Dealer hand:{} Current bet:{} Earning ratio:{}"
                                  "Earning:{} Current Money:{}".format(self.round, self.players[i].hand,
                                                                       self.dealer_hand, self.players[i].bet, ratio,
                                                                       earning, self.players[i].money))
                return True
            else:
                # players play the hand
                action = self.players[i].apply_basic_strategy(self.players[i].hand, self.dealer_hand[0])
                if not self.play_round_player(action, self.players[i]):
                    # card index reached.
                    self.index = self.deck_length
                    return False
        # dealer play. if all players lost, no need to play.
        if not all(player.status == "lost" for player in self.players):
            if not self.play_round_dealer():
                # card index reached.
                self.index = self.deck_length
                return False
            for i in range(self.player_num):
                if self.players[i].status is "lost":
                    continue
                self.finish_round(self.players[i])
        return True


    def play_game(self):
        """
        Play rounds consecutively as long as cards available.
        :return:
        """
        while self.cut_card > self.index and self.index < self.deck_length:
            # self.index += 1  # burning the first card.
            self.round += 1
            self.play_round()

if __name__ == '__main__':

    game = Game(1, 100, 1, 8, "debug")
    xlist = list()
    # keep playing as long as money is above 80
    while game.players[0].money > 80:
        # keep playing if there is card
        if game.index < game.cut_card and game.index < game.deck_length:
            game.round += 1
            if game.play_round():
                xlist.append(game.players[0].money)
            else:
                game = Game(1, game.players[0].money, 1, 8, "debug")
    print(xlist)