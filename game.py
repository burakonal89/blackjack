import numpy as np
import logging
from Player import Player
from Hand import Hand

class Game:
    """
    description goes here.
    """
    def __init__(self,
                 players,
                 start_moneys,
                 bet,
                 number_of_decks,
                 logging_level="warning",
                 dealer_threshold=17):
        """
        :param players: list of strings, indicating player strategy.
        e.g. ['basic strategy', 'card counting', 'random']
        :param logging_level: CRITICAL 50
                              ERROR 40
                              WARNING 30
                              INFO 20
                              DEBUG 10
                              NOTSET 0
        """
        self.logger = logging
        numeric_level = getattr(logging, logging_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: {}'.format(logging_level))
        self.logger.basicConfig(level=numeric_level)
        self.index = 0
        self.round = 0
        self.players = []
        self.bet = bet
        self.number_of_players = len(players)
        self.id = -1
        self.hands = {i: [Hand(self.bet)] for i in range(self.number_of_players)}
        self.hands[self.id] = []
        for i, player, start_money in zip(range(self.number_of_players), players, start_moneys):
            self.players.append(Player(player, start_money, i, self.hands))
        self.deck = np.repeat(np.arange(1, 14), 4 * number_of_decks)
        self.deck_length = len(self.deck)
        # inline shuffle
        np.random.shuffle(self.deck)
        self.ratios = {"blackjack": 1.5,
                       "win": 1,
                       "push": 0,
                       "lost": -1,
                       "insurance": np.NaN}
        self.cut_card = np.random.randint(low=int(self.deck_length / 2), high=int(self.deck_length))
        self.index = 0  # index, to keep track of the cards in the deck
        self.game_round = 0  # to keep track of the game
        self.logger.info("The game starts.\n"
                         "Deck: {}\n"
                         "The ratios:{}\n"
                         "The deck length:{}\n"
                         "Cut card position:{}".format(self.deck, self.ratios, self.deck_length, self.cut_card))

    def cut_card_reached(self):
        """
        check cut card reached.
        #TODO: you can pop card from self.deck.pop(0) each time. But you can't keep track of the deck for debugging
        #TODO: purposes. Or can you somehow?
        """
        if self.index == self.cut_card:
            self.logger.info("Cut card reached at index: {}\n"
                             "Game terminating.".format(self.index))
            return True
        return False

    def update_hands(self):
        """
        Updates hands of each players and the dealer.\
        """
        for player in self.players:
            player.hands = self.hands

    def distribute_cards(self):

        """
        Distributes cards to each players and the dealer.
        """
        # initialise player and hands
        self.hands = {i: [Hand(self.bet)] for i in range(self.number_of_players)}
        self.hands[self.id] = []
        # update player hand
        for player in self.players:
            player.hands = self.hands
        for _ in range(2):
            for i, player in enumerate(self.players):
                if not self.hands[i][0].hand:
                    self.hands[i][0].hand = [self.deck[self.index]]
                else:
                    self.hands[i][0].hand.append(self.deck[self.index])
                self.index += 1
                if self.cut_card_reached():
                    return False
            if not self.hands[self.id]:
                self.hands[self.id] = [self.deck[self.index]]
            else:
                self.hands[self.id].append(self.deck[self.index])
            self.index += 1
            if self.cut_card_reached():
                return False
        return True

    @staticmethod
    def hand_sum(hand):
        """
        description goes here.
        """
        hand_ = [min(10, card) for card in hand]
        sum_1 = sum(hand_)
        sum_2 = sum_1
        if 1 in hand_:
            sum_2 = sum_1+10
        if sum_1 <= 21 and sum_2 <= 21:
            return max(sum_1, sum_2)
        return min(sum_1, sum_2)

    @staticmethod
    def calculate_hand_status(hand):
        """
        Ace can worth 1 or 11 depending on the hand.
        :param hand: List of cards from players or the dealer
        :return: closest sum to 21
        """

        # check blackjack
        hand_ = [min(10, card) for card in hand.hand]
        hand.sum = Game.hand_sum(hand.hand)
        if hand_ == [1, 10] or hand_ == [10, 1]:
            hand.status = "blackjack"
        if hand.sum == 21:
            hand.status = "win"
        elif hand.sum > 21:
            hand.status = "lost"

    def update_dealer_hand(self):
        """

        """
        dealer_sum = self.hand_sum(self.hands[self.id])
        while dealer_sum < 17:
            self.hands[self.id].append(self.deck[self.index])
            self.index += 1
            if self.cut_card_reached():
                return False
            dealer_sum = self.hand_sum(self.hands[self.id])
        return True

    def evaluate_round(self):
        """

        """
        if not self.update_dealer_hand():
            return False
        self.logger.debug("Round-{} dealer hand: {}.".format(self.game_round,self.hands[self.id]))
        dealer_sum = self.hand_sum(self.hands[self.id])
        dealer_hand = [min(x, 10) for x in self.hands[self.id]]
        for player in self.players:
            for hand in self.hands[player.id]:
                if hand.status == 'discard':
                    continue
                if hand.status == "lost":
                    player.start_money += self.ratios["lost"]*hand.bet
                elif hand.status == "blackjack":
                    if dealer_hand == [1, 10] or dealer_hand == [10, 1]:
                        player.start_money += self.ratios["push"] * hand.bet
                        hand.status = 'push'
                    else:
                        player.start_money += self.ratios["blackjack"] * hand.bet
                elif hand.status == "win":
                    if dealer_sum == 21:
                        player.start_money += self.ratios["push"] * hand.bet
                        hand.status = 'push'
                    else:
                        player.start_money += self.ratios["win"] * hand.bet
                elif not hand.status:
                    if dealer_sum > 21 or dealer_sum < hand.sum:
                        player.start_money += self.ratios["win"] * hand.bet
                        hand.status = 'win'
                    elif dealer_sum == hand.sum:
                        player.start_money += self.ratios["push"] * hand.bet
                        hand.status = 'push'
                    elif dealer_sum > hand.sum:
                        player.start_money += self.ratios["lost"] * hand.bet
                        hand.status = 'lost'
                    else:
                        self.logger.error("Round-{} Player:{}\tno evaluation.".format(self.game_round,
                                                                                           player.id + 1))
                        raise ValueError
                else:
                    self.logger.error("Round-{} Player:{}\tno evaluation.".format(self.game_round,
                                                                                  player.id + 1))
                    raise ValueError
        return True

    def play_round(self):
        """
        description goes here.
        """
        self.game_round += 1
        self.logger.debug("Round-{} starts".format(self.game_round))
        if not self.distribute_cards():
            return False
        # debug
        # self.hands[self.id] = [6, 7]
        # self.hands[0][0].hand = [1, 8]
        for player in self.players:
            for hand in self.hands[player.id]:
                while True:
                    if len(hand.hand) == 1:  # only one card in the hand, give card.
                        hand.hand.append(self.deck[self.index])
                        self.index += 1
                        if self.cut_card_reached():
                            return False
                    # assess hand, check if hand can continue
                    self.calculate_hand_status(hand)
                    self.logger.debug("Round-{} Player-{}\tstatus: {} hand: {}\tdealer upcard: {}".format(self.game_round,
                                                                                                          player.id+1,
                                                                                                          hand.status,
                                                                                                          hand.hand,
                                                                                                          self.hands[self.id]))
                    if hand.status in self.ratios.keys():
                        break
                    action = player.play(hand)
                    if not action:
                        self.logger.error("Round-{} Player:{}\tno action returned.".format(self.game_round,
                                                                                           player.id + 1))
                        raise ValueError
                    self.logger.debug("Round-{} Player:{}\taction: {}".format(self.game_round,
                                                                              player.id+1,
                                                                              action))
                    if action == "stand":
                        break
                    elif action == "hit" or action == "double":
                        if action == "double":
                            hand.bet *= 2
                        hand.hand.append(self.deck[self.index])
                        self.index += 1
                        if self.cut_card_reached():
                            return False
                        continue
                    elif action == "split":
                        #TODO maximum split is limited to 4
                        hand_0 = Hand(hand.bet)
                        hand_0.hand = [hand.hand[0]]
                        hand_1 = Hand(hand.bet)
                        hand_1.hand = [hand.hand[1]]
                        self.hands[player.id].append(hand_0)
                        self.hands[player.id].append(hand_1)
                        hand.status = 'discard'
                        break
        # evaluate round
        if not self.evaluate_round():
            return False
        # logging
        for player in self.players:
            hands = [hand.hand for hand in self.hands[player.id]]
            statoos = [hand.status for hand in self.hands[player.id]]
            bets = [hand.bet for hand in self.hands[player.id]]
            self.logger.debug("Round-{} Player:{}\thands: {}\tstatoos: {}\tbets: {}\tmoney: {}".format(self.game_round,
                                                                                                       player.id + 1,
                                                                                                       hands,
                                                                                                       statoos,
                                                                                                       bets,
                                                                                                       player.start_money))
        return True

    def play_game(self):
        """

        """
        while True:
            if not self.play_round():
                break


if __name__ == '__main__':

    game = Game(players=['basic', 'basic', 'basic'],
                start_moneys=[100,100,100],
                bet=1,
                number_of_decks=6,
                logging_level='debug')
    game.play_game()
