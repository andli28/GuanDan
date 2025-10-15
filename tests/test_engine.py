import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import Card, GuanDanGame, SimpleAgent, SUITS, RANKS

class TestGuanDanGame(unittest.TestCase):
    def setUp(self):
        self.game = GuanDanGame(["Player 1", "Player 2", "Player 3", "Player 4"])
        self.game.teams['A']['level'] = 2
        self.game.declarer_team = 'A'
        # Manually create a deck and assign card values for predictable testing
        self.game.deck = self._create_test_deck()
        self.game._assign_card_values()

    def _create_test_deck(self):
        """Creates a predictable deck for testing purposes."""
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append(Card(rank, suit))
        deck.append(Card('Black Joker', 'Joker'))
        deck.append(Card('Red Joker', 'Joker'))
        return deck

    def _get_card(self, rank_str, suit):
        """Finds and returns a specific card from the test deck."""
        card = next((c for c in self.game.deck if c.rank_str == rank_str and c.suit == suit), None)
        if card is None:
            self.fail(f"Card {rank_str} of {suit} not found in test deck.")
        return card

    def test_get_combination_details(self):
        # Single
        combo = [self._get_card('3', 'Hearts')]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'single')
        self.assertEqual(length, 1)

        # Pair
        combo = [self._get_card('4', 'Hearts'), self._get_card('4', 'Spades')]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'pair')
        self.assertEqual(length, 2)

        # Triple
        combo = [self._get_card('5', 'Hearts'), self._get_card('5', 'Spades'), self._get_card('5', 'Clubs')]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'triple')
        self.assertEqual(length, 3)

        # Full House
        combo = [
            self._get_card('6', 'Hearts'), self._get_card('6', 'Spades'), self._get_card('6', 'Clubs'),
            self._get_card('7', 'Diamonds'), self._get_card('7', 'Clubs')
        ]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'full_house')
        self.assertEqual(length, 5)

        # Straight
        combo = [
            self._get_card('3', 'Hearts'), self._get_card('4', 'Spades'), self._get_card('5', 'Clubs'),
            self._get_card('6', 'Diamonds'), self._get_card('7', 'Clubs')
        ]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'straight')
        self.assertEqual(length, 5)

        # Tube
        combo = [
            self._get_card('8', 'Hearts'), self._get_card('8', 'Spades'),
            self._get_card('9', 'Clubs'), self._get_card('9', 'Diamonds'),
            self._get_card('10', 'Hearts'), self._get_card('10', 'Clubs')
        ]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'tube')
        self.assertEqual(length, 6)

        # Plate
        combo = [
            self._get_card('J', 'Hearts'), self._get_card('J', 'Spades'), self._get_card('J', 'Clubs'),
            self._get_card('Q', 'Diamonds'), self._get_card('Q', 'Clubs'), self._get_card('Q', 'Spades')
        ]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'plate')
        self.assertEqual(length, 6)

        # Bomb
        combo = [
            self._get_card('A', 'Hearts'), self._get_card('A', 'Spades'),
            self._get_card('A', 'Clubs'), self._get_card('A', 'Diamonds')
        ]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'bomb')
        self.assertEqual(length, 4)

        # Straight Flush
        combo = [
            self._get_card('3', 'Spades'), self._get_card('4', 'Spades'), self._get_card('5', 'Spades'),
            self._get_card('6', 'Spades'), self._get_card('7', 'Spades')
        ]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'straight_flush')
        self.assertEqual(length, 5)

        # Joker Bomb
        combo = [self._get_card('Black Joker', 'Joker'), self._get_card('Red Joker', 'Joker')]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertEqual(combo_type, 'joker_bomb')
        self.assertEqual(length, 2)

        # Invalid Combination
        combo = [self._get_card('3', 'Hearts'), self._get_card('5', 'Spades')]
        combo_type, rank, length = self.game.get_combination_details(combo)
        self.assertIsNone(combo_type)

    def test_is_valid_play(self):
        # 1. Play on an empty table (any valid combo is fine)
        play = [self._get_card('5', 'Hearts')]
        self.assertTrue(self.game.is_valid_play(play))

        # 2. Play a higher-ranking combo of the same type
        self.game.current_trick.append([self._get_card('6', 'Hearts')])
        play = [self._get_card('7', 'Hearts')]
        self.assertTrue(self.game.is_valid_play(play))

        # 3. Play a lower-ranking combo of the same type
        self.game.current_trick = [[self._get_card('K', 'Diamonds')]]
        play = [self._get_card('Q', 'Spades')]
        self.assertFalse(self.game.is_valid_play(play))

        # 4. Play a bomb against a non-bomb
        self.game.current_trick = [[self._get_card('A', 'Spades')]]
        play = [
            self._get_card('3', 'Hearts'), self._get_card('3', 'Spades'),
            self._get_card('3', 'Clubs'), self._get_card('3', 'Diamonds')
        ]
        self.assertTrue(self.game.is_valid_play(play))

        # 5. Play a higher-ranking bomb against a lower-ranking bomb
        self.game.current_trick = [[
            self._get_card('4', 'Hearts'), self._get_card('4', 'Spades'),
            self._get_card('4', 'Clubs'), self._get_card('4', 'Diamonds')
        ]]
        play = [
            self._get_card('5', 'Hearts'), self._get_card('5', 'Spades'),
            self._get_card('5', 'Clubs'), self._get_card('5', 'Diamonds')
        ]
        self.assertTrue(self.game.is_valid_play(play))

        # 6. Play combo of a different type
        self.game.current_trick = [[self._get_card('8', 'Hearts'), self._get_card('8', 'Spades')]]
        play = [
            self._get_card('9', 'Hearts'), self._get_card('9', 'Spades'),
            self._get_card('9', 'Clubs')
        ]
        self.assertFalse(self.game.is_valid_play(play))

    def test_update_levels(self):
        # Mock players for ranking
        p1 = self.game.players[0] # Team A
        p2 = self.game.players[1] # Team B
        p3 = self.game.players[2] # Team A
        p4 = self.game.players[3] # Team B

        # Scenario 1: Team A finishes 1st and 2nd -> Team A levels up by 3
        rankings = [p1, p3, p2, p4]
        self.game.teams['A']['level'] = 5
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 8)

        # Scenario 2: Team B finishes 1st and 3rd -> Team B levels up by 2
        rankings = [p2, p1, p4, p3]
        self.game.teams['B']['level'] = 3
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['B']['level'], 5)

        # Scenario 3: Team A finishes 1st and 4th -> Team A levels up by 1
        rankings = [p1, p2, p4, p3]
        self.game.teams['A']['level'] = 9
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 10)

        # Scenario 4: Leveling up is capped at 14 (Ace)
        rankings = [p1, p3, p2, p4]
        self.game.teams['A']['level'] = 12
        self.game.update_levels(rankings)
        self.assertEqual(self.game.teams['A']['level'], 14)

        # Scenario 5: Winning the game
        self.game.teams['A']['level'] = 14
        game_over = self.game.update_levels(rankings)
        self.assertTrue(game_over)

class TestSimpleAgent(unittest.TestCase):
    def setUp(self):
        self.game = GuanDanGame(["Agent", "Player 2", "Player 3", "Player 4"])
        self.game.teams['A']['level'] = 2
        self.game.declarer_team = 'A'
        self.game.deck = self._create_test_deck()
        self.game._assign_card_values()

        self.agent = SimpleAgent("Agent", "A")
        self.game.players[0] = self.agent

    def _create_test_deck(self):
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append(Card(rank, suit))
        deck.append(Card('Black Joker', 'Joker'))
        deck.append(Card('Red Joker', 'Joker'))
        return deck

    def _get_card(self, rank_str, suit):
        card = next((c for c in self.game.deck if c.rank_str == rank_str and c.suit == suit), None)
        if card is None:
            self.fail(f"Card {rank_str} of {suit} not found in test deck.")
        return card

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
