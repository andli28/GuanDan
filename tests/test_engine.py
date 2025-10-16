import unittest

from src.engine import Card, GuanDanGame, SimpleAgent, SUITS, RANKS

class GuanDanTestBase(unittest.TestCase):
    def setUp(self):
        # This setup will be inherited by all test classes
        self.game = GuanDanGame(["Player 1", "Player 2", "Player 3", "Player 4"])
        self.game.teams['A']['level'] = 2
        self.game.declarer_team = 'A'
        # Manually create a deck and assign card values for predictable testing
        self.game.deck = self._create_test_deck()
        self.game._assign_card_values()

    def _create_test_deck(self):
        """Creates a predictable double deck for testing purposes."""
        deck = []
        for _ in range(2): # Two decks
            for suit in SUITS:
                for rank in RANKS:
                    deck.append(Card(rank, suit))
            deck.append(Card('Black Joker', 'Joker'))
            deck.append(Card('Red Joker', 'Joker'))
        return deck

    def _get_cards(self, rank_str, suit, count=1):
        """Finds and returns a specific number of cards from the test deck."""
        cards = [c for c in self.game.deck if c.rank_str == rank_str and c.suit == suit]
        if len(cards) < count:
            self.fail(f"Could not find {count} cards of {rank_str} of {suit} in test deck.")
        return cards[:count]

    def _get_card(self, rank_str, suit):
        """Convenience method to get a single card."""
        return self._get_cards(rank_str, suit, 1)[0]

class TestGuanDanGame(GuanDanTestBase):
    def test_get_combination_details(self):
        with self.subTest(msg="Single"):
            combo = [self._get_card('3', 'Hearts')]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'single')
            self.assertEqual(length, 1)

        with self.subTest(msg="Pair"):
            combo = [self._get_card('4', 'Hearts'), self._get_card('4', 'Spades')]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'pair')
            self.assertEqual(length, 2)

        with self.subTest(msg="Triple"):
            combo = [self._get_card('5', 'Hearts'), self._get_card('5', 'Spades'), self._get_card('5', 'Clubs')]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'triple')
            self.assertEqual(length, 3)

        with self.subTest(msg="Full House"):
            combo = [
                self._get_card('6', 'Hearts'), self._get_card('6', 'Spades'), self._get_card('6', 'Clubs'),
                self._get_card('7', 'Diamonds'), self._get_card('7', 'Clubs')
            ]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'full_house')
            self.assertEqual(length, 5)

        with self.subTest(msg="Straight"):
            combo = [
                self._get_card('3', 'Hearts'), self._get_card('4', 'Spades'), self._get_card('5', 'Clubs'),
                self._get_card('6', 'Diamonds'), self._get_card('7', 'Clubs')
            ]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'straight')
            self.assertEqual(length, 5)

        with self.subTest(msg="Tube"):
            combo = [
                self._get_card('8', 'Hearts'), self._get_card('8', 'Spades'),
                self._get_card('9', 'Clubs'), self._get_card('9', 'Diamonds'),
                self._get_card('10', 'Hearts'), self._get_card('10', 'Clubs')
            ]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'tube')
            self.assertEqual(length, 6)

        with self.subTest(msg="Plate"):
            combo = [
                self._get_card('J', 'Hearts'), self._get_card('J', 'Spades'), self._get_card('J', 'Clubs'),
                self._get_card('Q', 'Diamonds'), self._get_card('Q', 'Clubs'), self._get_card('Q', 'Spades')
            ]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'plate')
            self.assertEqual(length, 6)

        with self.subTest(msg="Bomb"):
            combo = [
                self._get_card('A', 'Hearts'), self._get_card('A', 'Spades'),
                self._get_card('A', 'Clubs'), self._get_card('A', 'Diamonds')
            ]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'bomb')
            self.assertEqual(length, 4)

        with self.subTest(msg="Straight Flush"):
            combo = [
                self._get_card('3', 'Spades'), self._get_card('4', 'Spades'), self._get_card('5', 'Spades'),
                self._get_card('6', 'Spades'), self._get_card('7', 'Spades')
            ]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'straight_flush')
            self.assertEqual(length, 5)

        with self.subTest(msg="Joker Bomb"):
            combo = [self._get_card('Black Joker', 'Joker'), self._get_card('Red Joker', 'Joker')]
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'joker_bomb')
            self.assertEqual(length, 2)

        with self.subTest(msg="Invalid Combination"):
            combo = [self._get_card('3', 'Hearts'), self._get_card('5', 'Spades')]
            combo_type, _, _ = self.game.get_combination_details(combo)
            self.assertIsNone(combo_type)

        with self.subTest(msg="5-Card Bomb"):
            # This test is only possible with a double deck
            combo = self._get_cards('A', 'Hearts', 2) + self._get_cards('A', 'Spades', 2) + self._get_cards('A', 'Clubs', 1)
            combo_type, _, length = self.game.get_combination_details(combo)
            self.assertEqual(combo_type, 'bomb')
            self.assertEqual(length, 5)

    def test_is_valid_play_on_empty_table(self):
        play = [self._get_card('5', 'Hearts')]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_higher_rank_same_type(self):
        self.game.current_trick.append([self._get_card('6', 'Hearts')])
        play = [self._get_card('7', 'Hearts')]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_lower_rank_same_type(self):
        self.game.current_trick = [[self._get_card('K', 'Diamonds')]]
        play = [self._get_card('Q', 'Spades')]
        self.assertFalse(self.game.is_valid_play(play))

    def test_is_valid_play_bomb_beats_non_bomb(self):
        self.game.current_trick = [[self._get_card('A', 'Spades')]]
        play = [
            self._get_card('3', 'Hearts'), self._get_card('3', 'Spades'),
            self._get_card('3', 'Clubs'), self._get_card('3', 'Diamonds')
        ]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_higher_bomb_beats_lower_bomb(self):
        self.game.current_trick = [[
            self._get_card('4', 'Hearts'), self._get_card('4', 'Spades'),
            self._get_card('4', 'Clubs'), self._get_card('4', 'Diamonds')
        ]]
        play = [
            self._get_card('5', 'Hearts'), self._get_card('5', 'Spades'),
            self._get_card('5', 'Clubs'), self._get_card('5', 'Diamonds')
        ]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_different_type_is_invalid(self):
        self.game.current_trick = [[self._get_card('8', 'Hearts'), self._get_card('8', 'Spades')]]
        play = [
            self._get_card('9', 'Hearts'), self._get_card('9', 'Spades'),
            self._get_card('9', 'Clubs')
        ]
        self.assertFalse(self.game.is_valid_play(play))

    def test_update_levels_1st_and_2nd(self):
        p1, p2, p3, p4 = self.game.players[0], self.game.players[1], self.game.players[2], self.game.players[3]
        rankings = [p1, p3, p2, p4]
        self.game.teams['A']['level'] = 5
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 8)

    def test_update_levels_1st_and_3rd(self):
        p1, p2, p3, p4 = self.game.players[0], self.game.players[1], self.game.players[2], self.game.players[3]
        rankings = [p2, p1, p4, p3]
        self.game.teams['B']['level'] = 3
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['B']['level'], 5)

    def test_update_levels_1st_and_4th(self):
        p1, p2, p3, p4 = self.game.players[0], self.game.players[1], self.game.players[2], self.game.players[3]
        rankings = [p1, p2, p4, p3]
        self.game.teams['A']['level'] = 9
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 10)

    def test_update_levels_capped_at_14(self):
        p1, p3 = self.game.players[0], self.game.players[2]
        rankings = [p1, p3]
        self.game.teams['A']['level'] = 12
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 14)

    def test_update_levels_wins_game(self):
        p1, p3 = self.game.players[0], self.game.players[2]
        rankings = [p1, p3]
        self.game.teams['A']['level'] = 14
        game_over = self.game.update_levels(rankings)
        self.assertTrue(game_over)

class TestSimpleAgent(GuanDanTestBase):
    def setUp(self):
        # Call the parent setup first
        super().setUp()
        # Additional setup specific to the agent tests
        self.agent = SimpleAgent("Agent", "A")
        self.game.players[0] = self.agent

    def test_find_best_play_selects_lowest_valid_play(self):
        # Give the agent a hand with multiple valid plays
        self.agent.hand = [
            self._get_card('3', 'Hearts'),
            self._get_card('5', 'Spades'), self._get_card('5', 'Clubs'),
            self._get_card('8', 'Diamonds'),
        ]
        self.agent.sort_hand()
        self.game.current_trick.append([self._get_card('4', 'Hearts')])

        play = self.agent.find_best_play(self.game)

        # The lowest valid play is the '5 of Spades' (value 5)
        self.assertEqual(len(play), 1)
        self.assertEqual(play[0].rank_str, '5')

    def test_find_best_play_passes_when_no_valid_move(self):
        # Give the agent a hand with no valid plays
        self.agent.hand = [self._get_card('3', 'Hearts'), self._get_card('4', 'Spades')]
        self.agent.sort_hand()
        self.game.current_trick.append([self._get_card('K', 'Clubs')])

        play = self.agent.find_best_play(self.game)

        # Agent should pass (return an empty list)
        self.assertEqual(len(play), 0)

if __name__ == '__main__':
    unittest.main()
