# -*- coding: utf-8 -*-
__author__ = "burakonal"

import numpy as np
import logging
from player import Player
from hand import Hand
from dealer import Dealer


class Game:
    # Calls Player and Dealer classes and generates players.
    # Plays the game.
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
        # inline shuffle
        np.random.shuffle(self.deck)
        # ratios. Subject to change.
        self.ratios = {"blackjack": 1.5, "win": 1, "push": 0, "lost": -1, "insurance": np.NaN}
        # make sure cut card put in the second half of the cards.
        self.cut_card = np.random.randint(low=int(self.deck_length / 2), high=int(self.deck_length))
        self.logger.info("The game starts.\n"
                         "Deck: {}\n"
                         "The ratios:{}\n"
                         "The deck length:{}\n"
                         "Cut card position:{}".format(self.deck, self.ratios, self.deck_length, self.cut_card))
        self.players = list()
        # generate players and add them into game.
        for i in range(player_num):
            self.players.append(Player(start_money))
        self.dealer = Dealer()
        self.dealer.threshold = dealer_threshold
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


    @staticmethod
    def calculate_round(ratio, money, bet):
        earning = bet * ratio
        money = money + earning
        return earning, money


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
            hand[np.where(hand == 11)[0][0]] = 1
        if abs(21-curr_sum) < abs(21-prev_sum) and curr_sum < 21:
            return curr_sum
        return prev_sum


    def play_round_dealer(self):
        """
        Play one round for the dealer.
        :return:
        """
        if self.is_blackjack(self.dealer.hand):
            self.dealer.status = "blackjack"
            return
        self.dealer.sum = self.hand_sum(self.dealer.hand)
        while self.dealer.sum < self.dealer.threshold:
            if self.index+1 >= self.cut_card:
                self.logger.debug("Round: {}\t Current index: {}\t. Cut card:{}\tThe game ends.".format(self.round,
                                                                                                        self.index,
                                                                                                        self.cut_card))
                return False
            self.dealer.hand = np.append(self.dealer.hand, self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            self.logger.debug("Round:{}\tDealer hit.\tDealer hand:{}".format(self.round, self.dealer.hand))
            self.dealer.sum = self.hand_sum(self.dealer.hand)
            if self.dealer.sum > 21:
                self.dealer.status = "lost"
                return True
        self.dealer.status = "wait"
        return True

    def play_round_player(self, action, hand, player):
        """
        Play one round of the game for a player.
        :param action: action for the hand. One of double, split, hit, stand.
        :param hand: instance of hand class
        :param player: instance of player class
        :return: Boolean, false if index is out of deck.
        """
        if action == "stand":
            self.logger.debug("Round:{}\tPlayer stands.\tPlayer hand:{}\tDealer hand:{}".format(self.round, hand.hand,
                                                                                                self.dealer.hand))
            if self.is_blackjack(hand.hand):
                hand.status = "blackjack"
            else:
                hand.status = "wait"
            return True
        elif action == "hit":
            if self.index+1 >= self.cut_card:
                self.logger.debug("Round: {}\t Current index: {}\t. Cut card:{}\tThe game ends.".format(self.round,
                                                                                                        self.index,
                                                                                                        self.cut_card))
                return False
            hand.hand = np.append(hand.hand, self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            self.logger.debug("Round:{}\tPlayer hit.\tPlayer hand:{}\tDealer hand:{}".format(self.round, hand.hand,
                                                                                             self.dealer.hand))
            hand.sum = self.hand_sum(hand.hand)
            # busted
            if hand.sum > 21:
                hand.status = "lost"
                return True
            else:
                action = Player.apply_basic_strategy(hand.hand, self.dealer.hand[0])
                return self.play_round_player(action, hand, player)

        elif action == "double":
            if self.index+1 >= self.cut_card:
                self.logger.debug("Round: {}\t Current index: {}\t. Cut card:{}\tThe game ends.".format(self.round,
                                                                                                        self.index,
                                                                                                        self.cut_card))
                return False
            hand.bet = 2*hand.bet
            hand.hand = np.append(hand.hand, self.ceil_to_10(self.deck[self.index]))
            self.index += 1
            self.logger.debug("Round:{}\tPlayer doubled.\tPlayer hand:{}\tDealer hand:{}".format(self.round, hand.hand,
                                                                                                 self.dealer.hand))
            hand.sum = self.hand_sum(hand.hand)
            # busted
            if hand.sum > 21:
                hand.status = "lost"
            else:
                hand.status = "wait"
            return True

        elif action == "split":
            if self.index+1 >= self.cut_card:
                self.logger.debug("Round: {}\t Current index: {}\t. Cut card:{}\tThe game ends.".format(self.round,
                                                                                                        self.index,
                                                                                                        self.cut_card))
                return False
            second_hand = Hand()
            second_hand.status = "wait"
            second_hand.bet = hand.bet
            second_hand.hand = np.array([hand.hand[0]])
            hand.hand = np.array([hand.hand[0], self.ceil_to_10(self.deck[self.index])])
            self.index += 1
            self.logger.debug("Round:{}\tPlayer split.\tPlayer hand:{}\tDealer hand:{}".format(self.round, hand.hand,
                                                                                               self.dealer.hand))
            action = Player.apply_basic_strategy(hand.hand, self.dealer.hand[0])
            if not self.play_round_player(action, hand, player):
                return False
            if self.index+1 >= self.cut_card:
                self.logger.debug("Round: {}\t Current index: {}\t. Cut card:{}\tThe game ends.".format(self.round,
                                                                                                        self.index,
                                                                                                        self.cut_card))
                return False
            second_hand.hand = np.append(second_hand.hand, self.ceil_to_10(self.deck[self.index]))
            second_hand.sum = self.hand_sum(second_hand.hand)
            self.index += 1
            self.logger.debug("Round:{}\tPlayer split.\tPlayer hand:{}\tDealer hand:{}".format(self.round, second_hand.hand,
                                                                                               self.dealer.hand))
            player.hands.append(second_hand)
            action = Player.apply_basic_strategy(second_hand.hand, self.dealer.hand[0])
            return self.play_round_player(action, second_hand, player)

    def finish_round(self, hand, player):
        """
        Finish round by comparing dealer hand with player's single hand.
        Note that due to split, there might be more than one hand in the player.

        :param hand: Instance of the hand class.
        :return:
        """
        if hand.status == "lost":
            ratio = self.ratios["lost"]
            earning, money = self.calculate_round(ratio, player.money, hand.bet)
            player.money = money
            self.logger.debug("Round:{}\tLost\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                              "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand, hand.bet,
                                                                    ratio, earning, player.money))
        # player got blackjack
        elif hand.status == "blackjack":
            if self.dealer.status == "blackjack":
                ratio = self.ratios["push"]
                earning, money = self.calculate_round(ratio, player.money, hand.bet)
                player.money = money
                self.logger.debug("Round:{}\tPush\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand, hand.bet,
                                                                        ratio, earning, player.money))
            else:
                ratio = self.ratios["blackjack"]
                earning, money = self.calculate_round(ratio, player.money, hand.bet)
                player.money = money
                self.logger.debug("Round:{}\tBlackJack\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand, hand.bet,
                                                                        ratio, earning, player.money))
        elif self.dealer.status == "lost":
            ratio = self.ratios["win"]
            earning, money = self.calculate_round(ratio, player.money, hand.bet)
            player.money = money
            self.logger.debug("Round:{}\tWin\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                              "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand, hand.bet,
                                                                    ratio, earning, player.money))
        elif self.dealer.status == "wait" and hand.status == "wait":
            if 21 - self.dealer.sum > 21 - hand.sum:
                ratio = self.ratios["win"]
                earning, money = self.calculate_round(ratio, player.money, hand.bet)
                player.money = money
                self.logger.debug("Round:{}\tWin\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand,
                                                                        hand.bet,
                                                                        ratio, earning, player.money))
            elif 21 - hand.sum > 21 - self.dealer.sum:
                ratio = self.ratios["lost"]
                earning, money = self.calculate_round(ratio, player.money, hand.bet)
                player.money = money
                self.logger.debug("Round:{}\tLost\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand,
                                                                        hand.bet,
                                                                        ratio, earning, player.money))
            else:
                ratio = self.ratios["push"]
                earning, money = self.calculate_round(ratio, player.money, hand.bet)
                player.money = money
                self.logger.debug("Round:{}\tPush\tPlayer hand:{}\tDealer hand:{}\tCurrent bet:{}\tEarning ratio:{}\t"
                                  "Earning:{}\tCurrent Money:{}".format(self.round, hand.hand, self.dealer.hand,
                                                                        hand.bet,
                                                                        ratio, earning, player.money))

    def play_round(self):
        """
        Play one round of the game for each player's hand and finally for the dealer.

        :return: updated card index, player(s) money.
        """

        # check if enough cards available for the current round.
        if self.index + 2 * (self.player_num + 1) >= self.deck_length:
            self.logger.debug("Round: {}\t Current index: {}. Cards cannot be distributed. The game finishes. "
                              "The index is set to deck length:{}.".format(self.round, self.index, self.deck_length))
            self.index = self.deck_length
            return False
        for i, player in enumerate(self.players):
            # TODO: each player can set up a new bet for each round. Currently playing with the minimum bet.
            hand = Hand()
            # deck[1,2]
            hand.hand = self.ceil_to_10(self.deck[[self.index + i, self.index + self.player_num + 1 + i]])
            hand.sum = self.hand_sum(hand.hand)
            hand.bet = self.bet
            hand.status = "wait"
            player.hands = list()
            player.hands.append(hand)
            self.logger.debug("Round:{}\tPlayer-{} hand:{}".format(self.round, i, player.hands[0].hand))
        self.dealer.hand = self.ceil_to_10(self.deck[[self.index + self.player_num, self.index + 2 * self.player_num + 1]])
        self.dealer.sum = self.hand_sum(self.dealer.hand)
        self.logger.debug("Round:{}\tDealer hand:{}".format(self.round, self.dealer.hand))
        self.index += (self.player_num + 1) * 2
        # play game for each player
        for player in self.players:
            action = Player.apply_basic_strategy(player.hands[0].hand, self.dealer.hand[0])
            if not self.play_round_player(action, player.hands[0], player):
                return False
        # if all hands lost, no need to play for the dealer.
        if not all(hand.status == "lost" for player in self.players for hand in player.hands):
            if not self.play_round_dealer():
                return False
        for player in self.players:
            for hand in player.hands:
                self.finish_round(hand, player)

        return True

    def play_game(self):
        """
        Plays one full game. A full game is playing rounds consecutively as long as cards available.
        :return:
        """
        while self.index < self.cut_card and self.index < self.deck_length:
            # self.index += 1  # burning the first card.
            self.round += 1
            self.play_round()


if __name__ == '__main__':

    game = Game(1, 100, 1, 8, "debug")
    game.deck[0] = 6
    game.deck[1] = 10
    game.deck[2] = 10
    game.deck[3] = 4
    game.deck[4] = 1
    game.deck[5] = 10
    game.play_game()