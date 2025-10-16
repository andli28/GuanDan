import unittest

from src.engine import Card, GuanDanGame, SimpleAgent, SUITS, RANKS


"""Unit tests for the Guan Dan game engine.

This module contains tests for the game logic, including combination validation,
play validation, scoring, and the simple agent's decision-making process.
"""


class GuanDanTestBase(unittest.TestCase):
    """A base class for Guan Dan tests that provides common setup logic.

    This class sets up a predictable game state with a non-shuffled double
    deck, allowing tests to reliably retrieve specific cards. It also
    pre-processes the deck into a lookup dictionary for efficient card access.
    """
    def setUp(self):
        """Sets up the test environment before each test.

        Initializes a game, sets a default level, creates a predictable deck,
        and builds a card lookup table for easy card retrieval.
        """
        # This setup will be inherited by all test classes
        self.game = GuanDanGame(["Player 1", "Player 2", "Player 3", "Player 4"])
        self.game.teams['A']['level'] = 2
        self.game.declarer_team = 'A'
        # Manually create a deck and assign card values for predictable testing
        self.game.deck = self._create_test_deck()
        self.game._assign_card_values()

        # Pre-process the deck for efficient O(1) card lookups in tests
        self.card_lookup = {}
        for card in self.game.deck:
            self.card_lookup.setdefault((card.rank_str, card.suit), []).append(card)

    def _create_test_deck(self):
        """Creates a predictable, un-shuffled double deck for testing."""
        deck = []
        for _ in range(2): # Two decks
            for suit in SUITS:
                for rank in RANKS:
                    deck.append(Card(rank, suit))
            deck.append(Card('Black Joker', 'Joker'))
            deck.append(Card('Red Joker', 'Joker'))
        return deck

    def _get_cards(self, rank_str, suit, count=1):
        """Retrieves a specific number of cards from the test deck.

        Uses the pre-processed `card_lookup` table for efficient access.

        Args:
            rank_str (str): The rank of the card to find.
            suit (str): The suit of the card to find.
            count (int): The number of cards to retrieve.

        Returns:
            list[Card]: A list of the requested cards.
        """
        key = (rank_str, suit)
        cards = self.card_lookup.get(key, [])
        if len(cards) < count:
            self.fail(f"Could not find {count} cards of {rank_str} of {suit} in test deck.")
        return cards[:count]

    def _get_card(self, rank_str, suit):
        """A convenience method to retrieve a single card from the test deck.

        Args:
            rank_str (str): The rank of the card to find.
            suit (str): The suit of the card to find.

        Returns:
            Card: The requested card object.
        """
        return self._get_cards(rank_str, suit, 1)[0]

class TestGuanDanGame(GuanDanTestBase):
    """Tests for the main GuanDanGame class and its core logic."""
    def test_get_combination_details(self):
        """Verifies that all valid card combinations are correctly identified."""
        with self.subTest(msg="Single"):
            combo = [self._get_card('3', 'Hearts')]
            self.assertEqual(self.game.get_combination_details(combo), ('single', 3, 1))

        with self.subTest(msg="Pair"):
            combo = [self._get_card('4', 'Hearts'), self._get_card('4', 'Spades')]
            self.assertEqual(self.game.get_combination_details(combo), ('pair', 20 + 4, 2))

        with self.subTest(msg="Triple"):
            combo = [self._get_card('5', 'Hearts'), self._get_card('5', 'Spades'), self._get_card('5', 'Clubs')]
            self.assertEqual(self.game.get_combination_details(combo), ('triple', 40 + 5, 3))

        with self.subTest(msg="Full House"):
            combo = [
                self._get_card('6', 'Hearts'), self._get_card('6', 'Spades'), self._get_card('6', 'Clubs'),
                self._get_card('7', 'Diamonds'), self._get_card('7', 'Clubs')
            ]
            self.assertEqual(self.game.get_combination_details(combo), ('full_house', 60 + 6, 5))

        with self.subTest(msg="Straight"):
            combo = [
                self._get_card('3', 'Hearts'), self._get_card('4', 'Spades'), self._get_card('5', 'Clubs'),
                self._get_card('6', 'Diamonds'), self._get_card('7', 'Clubs')
            ]
            self.assertEqual(self.game.get_combination_details(combo), ('straight', 80 + 7, 5))

        with self.subTest(msg="Tube"):
            combo = [
                self._get_card('8', 'Hearts'), self._get_card('8', 'Spades'),
                self._get_card('9', 'Clubs'), self._get_card('9', 'Diamonds'),
                self._get_card('10', 'Hearts'), self._get_card('10', 'Clubs')
            ]
            self.assertEqual(self.game.get_combination_details(combo), ('tube', 100 + 10, 6))

        with self.subTest(msg="Plate"):
            combo = [
                self._get_card('J', 'Hearts'), self._get_card('J', 'Spades'), self._get_card('J', 'Clubs'),
                self._get_card('Q', 'Diamonds'), self._get_card('Q', 'Clubs'), self._get_card('Q', 'Spades')
            ]
            self.assertEqual(self.game.get_combination_details(combo), ('plate', 120 + 12, 6))

        with self.subTest(msg="Bomb"):
            combo = [
                self._get_card('A', 'Hearts'), self._get_card('A', 'Spades'),
                self._get_card('A', 'Clubs'), self._get_card('A', 'Diamonds')
            ]
            self.assertEqual(self.game.get_combination_details(combo), ('bomb', 300 + 14, 4))

        with self.subTest(msg="Straight Flush"):
            combo = [
                self._get_card('3', 'Spades'), self._get_card('4', 'Spades'), self._get_card('5', 'Spades'),
                self._get_card('6', 'Spades'), self._get_card('7', 'Spades')
            ]
            self.assertEqual(self.game.get_combination_details(combo), ('straight_flush', 500 + 7, 5))

        with self.subTest(msg="Joker Bomb"):
            combo = [self._get_card('Black Joker', 'Joker'), self._get_card('Red Joker', 'Joker')]
            self.assertEqual(self.game.get_combination_details(combo), ('joker_bomb', 1000, 2))

        with self.subTest(msg="Invalid Combination"):
            combo = [self._get_card('3', 'Hearts'), self._get_card('5', 'Spades')]
            self.assertEqual(self.game.get_combination_details(combo), (None, 0, 0))

        with self.subTest(msg="5-Card Bomb"):
            # This test is only possible with a double deck
            combo = [c for c in self.game.deck if c.rank_str == 'A'][:5]
            self.assertEqual(self.game.get_combination_details(combo), ('bomb', 400 + 14, 5))

    def test_is_valid_play_on_empty_table(self):
        """Tests that any valid combination can be played on an empty table."""
        play = [self._get_card('5', 'Hearts')]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_higher_rank_same_type(self):
        """Tests that a higher-ranking play of the same type is valid."""
        self.game.current_trick.append([self._get_card('6', 'Hearts')])
        play = [self._get_card('7', 'Hearts')]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_lower_rank_same_type(self):
        """Tests that a lower-ranking play of the same type is invalid."""
        self.game.current_trick = [[self._get_card('K', 'Diamonds')]]
        play = [self._get_card('Q', 'Spades')]
        self.assertFalse(self.game.is_valid_play(play))

    def test_is_valid_play_bomb_beats_non_bomb(self):
        """Tests that a bomb can beat any non-bomb combination."""
        self.game.current_trick = [[self._get_card('A', 'Spades')]]
        play = [
            self._get_card('3', 'Hearts'), self._get_card('3', 'Spades'),
            self._get_card('3', 'Clubs'), self._get_card('3', 'Diamonds')
        ]
        self.assertTrue(self.game.is_valid_play(play))

    def test_is_valid_play_higher_bomb_beats_lower_bomb(self):
        """Tests that a higher-ranking bomb can beat a lower-ranking bomb."""
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
        """Tests that a non-bomb play cannot beat a play of a different type."""
        self.game.current_trick = [[self._get_card('8', 'Hearts'), self._get_card('8', 'Spades')]]
        play = [
            self._get_card('9', 'Hearts'), self._get_card('9', 'Spades'),
            self._get_card('9', 'Clubs')
        ]
        self.assertFalse(self.game.is_valid_play(play))

    def test_update_levels_1st_and_2nd(self):
        """Tests that team level increases by 3 for a 1st and 2nd place finish."""
        p1, p2, p3, p4 = self.game.players
        rankings = [p1, p3, p2, p4]
        self.game.teams['A']['level'] = 5
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 8)

    def test_update_levels_1st_and_3rd(self):
        """Tests that team level increases by 2 for a 1st and 3rd place finish."""
        p1, p2, p3, p4 = self.game.players
        rankings = [p2, p1, p4, p3]
        self.game.teams['B']['level'] = 3
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['B']['level'], 5)

    def test_update_levels_1st_and_4th(self):
        """Tests that team level increases by 1 for a 1st and 4th place finish."""
        p1, p2, p3, p4 = self.game.players
        rankings = [p1, p2, p4, p3]
        self.game.teams['A']['level'] = 9
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 10)

    def test_update_levels_capped_at_14(self):
        """Tests that team level is capped at 14 (Ace)."""
        p1, p2, p3, p4 = self.game.players
        rankings = [p1, p3, p2, p4]
        self.game.teams['A']['level'] = 12
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 14)

    def test_update_levels_wins_game(self):
        """Tests that update_levels returns True when a team wins at level Ace."""
        p1, p2, p3, p4 = self.game.players
        rankings = [p1, p3, p2, p4]
        self.game.teams['A']['level'] = 14
        game_over = self.game.update_levels(rankings)
        self.assertTrue(game_over)

class TestSimpleAgent(GuanDanTestBase):
    """Tests for the SimpleAgent player AI."""
    def setUp(self):
        """Sets up the agent test environment."""
        # Call the parent setup first
        super().setUp()
        # Additional setup specific to the agent tests
        self.agent = SimpleAgent("Agent", "A")
        self.game.players[0] = self.agent

    def test_find_best_play_selects_lowest_valid_play(self):
        """Tests that the agent selects the lowest-ranking valid move."""
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
        """Tests that the agent passes when it has no valid moves."""
        # Give the agent a hand with no valid plays
        self.agent.hand = [self._get_card('3', 'Hearts'), self._get_card('4', 'Spades')]
        self.agent.sort_hand()
        self.game.current_trick.append([self._get_card('K', 'Clubs')])

        play = self.agent.find_best_play(self.game)

        # Agent should pass (return an empty list)
        self.assertEqual(len(play), 0)

if __name__ == '__main__':
    unittest.main()
