import numpy as np
import logging
from player import Player
from hand import Hand

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
        self.hands = {i: [Hand(bet)] for i in range(self.number_of_players)}
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

    def calculate_hand_status(self,
                              hand):
        """
        Ace can worth 1 or 11 depending on the hand.
        :param hand: List of cards from players or the dealer
        :return: closest sum to 21
        """

        # check blackjack
        hand = [min(10, card) for card in hand]
        if hand == [1, 10] or hand == [10, 1]:
            return 'blackjack'
        sum_1 = sum(hand)
        if 1 in hand:
            hand2 = hand.copy()
            hand2[hand2.index(1)] = 11
            sum_2 = sum(hand2)
        else:
            sum_2 = sum_1
        if sum_1 == 21 or sum_2 == 21:
            return "win"
        elif sum_1 > 21 and sum_2 > 21:
            return "lose"
        return None

    def play_round(self):
        """
        description goes here.
        """
        self.game_round += 1
        for player in self.players:
            for hand in self.hands[player.id]:
                while True:
                    if len(hand.hand) == 1: # only one card in the hand, give card.
                        hand.hand.append(self.deck[self.index])
                        self.index += 1
                        if self.cut_card_reached():
                            return False
                    # assess hand, check if hand can continue
                    status = self.calculate_hand_status(hand.hand)
                    self.logger.debug("Round: {}\tPlayer:{}\tstatus: {} with hand:\t{}".format(self.game_round,
                                                                                               player.id,
                                                                                               hand.status,
                                                                                               hand.hand))
                    if status in self.ratios.keys():
                        hand.status = status
                        break
                    action = player.play(hand)
                    self.logger.debug("Round: {}\tPlayer:{} {} with hand:\t{}\tdealers hand: {}".format(self.game_round,
                                                                                                        player.id,
                                                                                                        action,
                                                                                                        hand.hand,
                                                                                                        self.hands[self.id]))
                    if action == "stand":
                        break
                    elif action == "hit":
                        hand.hand.append(self.deck[self.index])
                        self.index += 1
                        if self.cut_card_reached():
                            return False
                        continue
                    elif action == "double":
                        hand.bet *= 2
                        break
                    elif action == "split":
                        #TODO maximum split is limited to 4
                        hand_0 = Hand(hand.bet)
                        hand_0.hand = [hand.hand[0]]
                        hand_1 = Hand(hand.bet)
                        hand_1.hand = [hand.hand[1]]
                        self.hands[player.id].append(hand_0)
                        self.hands[player.id].append(hand_1)
                        continue
        return True

def play_game():
    pass

if __name__ == '__main__':

    game = Game(players=['basic', 'basic', 'basic'],
                start_moneys=[100,100,100],
                bet=1,
                number_of_decks=6,
                logging_level='debug')
    game.distribute_cards()
    game.play_round()
    game.play_round()
    game.play_round()
    game.play_round()
    game.play_round()
    game.play_round()
    game.play_round()


