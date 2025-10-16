import random
from collections import Counter
from itertools import combinations

# --- Card and Deck Configuration ---

SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14
}
# Special card values are handled dynamically based on the game's level.
# Red Joker > Black Joker > Level Card > Ace ...
JOKER_RANKS = {'Black Joker': 16, 'Red Joker': 17}

class Card:
    """Represents a single playing card."""
    def __init__(self, rank, suit):
        self.rank_str = str(rank)
        self.suit = suit
        self.value = 0 # This will be set dynamically by the game based on level
        self.is_wild = False

    def __repr__(self):
        if self.suit == 'Joker':
            return self.rank_str
        # Add a '*' to wild cards for easy identification
        return f"{self.rank_str} of {self.suit}{'*' if self.is_wild else ''}"

    def __lt__(self, other):
        return self.value < other.value

class Player:
    """Represents a player in the game."""
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.hand = []

    def sort_hand(self):
        """Sorts the player's hand based on card value."""
        self.hand.sort()

    def play_cards(self, cards_to_play):
        """Removes played cards from the player's hand."""
        for card in cards_to_play:
            # This removal logic is simple; more robust would be to match by value and suit
            for i, hand_card in enumerate(self.hand):
                if hand_card.rank_str == card.rank_str and hand_card.suit == card.suit:
                    self.hand.pop(i)
                    break
        return cards_to_play

class GuanDanGame:
    """Manages the state and rules of the Guan Dan game."""
    def __init__(self, player_names):
        self.players = [
            Player(player_names[0], 'A'),
            Player(player_names[1], 'B'),
            Player(player_names[2], 'A'),
            Player(player_names[3], 'B')
        ]
        self.teams = {'A': {'level': 2}, 'B': {'level': 2}}
        self.deck = []
        self.current_trick = []
        self.trick_winner = None
        self.turn_index = 0
        self.passes = 0
        self.declarer_team = None
        self.level_card_value = 0

    def _create_deck(self):
        """Creates a 108-card deck (2 standard decks + 4 jokers)."""
        self.deck = []
        for _ in range(2): # Two decks
            for suit in SUITS:
                for rank in RANKS:
                    self.deck.append(Card(rank, suit))
            # Add Jokers (2 per deck)
            self.deck.append(Card('Black Joker', 'Joker'))
            self.deck.append(Card('Red Joker', 'Joker'))
        random.shuffle(self.deck)

    def _assign_card_values(self):
        """Assigns numeric values to cards based on the current level."""
        # This must be called at the start of each hand.
        # Let's assume team A is the declarer for this logic, will need to be dynamic
        self.declarer_team = self.declarer_team or 'A' # Default to A for first hand
        level = self.teams[self.declarer_team]['level']
        self.level_card_value = 15 # Static value for the level card

        for card in self.deck:
            if card.suit == 'Joker':
                card.value = JOKER_RANKS[card.rank_str]
            elif RANKS.get(card.rank_str) == level:
                card.value = self.level_card_value
                if card.suit == 'Hearts':
                    card.is_wild = True
            else:
                card.value = RANKS.get(card.rank_str, 0)

    def deal(self):
        """Deals 27 cards to each of the four players."""
        self._create_deck()
        self._assign_card_values()
        for i in range(27):
            for player in self.players:
                player.hand.append(self.deck.pop())
        for player in self.players:
            player.sort_hand()

    def get_combination_details(self, cards):
        """Analyzes a combination of cards and returns its type, rank, and length."""
        if not cards:
            return None, 0, 0

        # This is a simplified validation logic. Wild cards add significant complexity.
        # For now, we ignore wild cards in combination detection.
        num_cards = len(cards)
        counts = Counter(c.value for c in cards)
        values = sorted(counts.keys())
        is_straight = len(values) == num_cards and (values[-1] - values[0] == num_cards - 1)

        # Joker Bomb
        if num_cards == 2 and {16, 17} == set(c.value for c in cards):
            return 'joker_bomb', 1000, 2

        is_flush = len(set(c.suit for c in cards)) == 1

        # Straight Flush (is a type of bomb)
        if num_cards == 5 and is_straight and is_flush:
            return 'straight_flush', 500 + values[-1], 5

        # Bomb
        if num_cards >= 4 and len(counts) == 1:
            base_rank = 0
            if num_cards == 4:
                base_rank = 300
            elif num_cards == 5:
                base_rank = 400
            else: # 6+ cards
                base_rank = num_cards * 100
            return 'bomb', base_rank + values[0], num_cards

        # Single
        if num_cards == 1:
            return 'single', values[0], 1
        # Pair
        if num_cards == 2 and len(counts) == 1:
            return 'pair', 20 + values[0], 2
        # Triple
        if num_cards == 3 and len(counts) == 1:
            return 'triple', 40 + values[0], 3
        # Full House
        if num_cards == 5 and sorted(counts.values()) == [2, 3]:
            triple_val = [v for v, c in counts.items() if c == 3][0]
            return 'full_house', 60 + triple_val, 5
        # Straight
        if num_cards == 5 and is_straight:
             return 'straight', 80 + values[-1], 5
        # Tube (3 consecutive pairs)
        if num_cards == 6 and len(counts) == 3 and all(c == 2 for c in counts.values()) and (values[2] - values[0] == 2):
            return 'tube', 100 + values[-1], 6
        # Plate (2 consecutive triples)
        if num_cards == 6 and len(counts) == 2 and all(c == 3 for c in counts.values()) and (values[1] - values[0] == 1):
            return 'plate', 120 + values[-1], 6

        return None, 0, 0 # Invalid combination

    def is_valid_play(self, play):
        """Checks if a play is valid against the current trick."""
        play_type, play_rank, play_len = self.get_combination_details(play)
        last_play = self.current_trick[-1] if self.current_trick else None

        if play_type is None:
            print("Debug: Invalid combination type.")
            return False

        # If the table is empty, any valid combination is fine.
        if last_play is None:
            return True

        last_play_type, last_play_rank, last_play_len = self.get_combination_details(last_play)

        is_play_bomb = play_type in ['bomb', 'straight_flush', 'joker_bomb']
        is_last_play_bomb = last_play_type in ['bomb', 'straight_flush', 'joker_bomb']

        # A bomb can beat any non-bomb.
        if is_play_bomb and not is_last_play_bomb:
            return True

        # if play is not a bomb, it cannot beat a bomb.
        if not is_play_bomb and is_last_play_bomb:
            return False

        if is_play_bomb and is_last_play_bomb:
            return play_rank > last_play_rank

        # For non-bombs, types must match.
        if play_type != last_play_type:
            return False

        # Rank must be higher.
        return play_rank > last_play_rank

    def play_turn(self, player_index, cards):
        """Processes a single player's turn."""
        player = self.players[player_index]
        if not cards: # Player passes
            self.passes += 1
            print(f"{player.name} passes.")
            if self.passes >= 3:
                print(f"--- {self.trick_winner.name} wins the trick and starts a new one. ---")
                self.current_trick = []
                self.passes = 0
                self.turn_index = self.players.index(self.trick_winner)
                return "TRICK_WON"
            self.turn_index = (self.turn_index + 1) % 4
            return "PASS"

        if self.is_valid_play(cards):
            player.play_cards(cards)
            self.current_trick.append(cards)
            self.trick_winner = player
            self.passes = 0
            print(f"{player.name} plays: {[str(c) for c in cards]}")
            self.turn_index = (self.turn_index + 1) % 4
            if not player.hand:
                return "HAND_WON"
            return "PLAYED"
        else:
            print(f"Invalid play by {player.name}. Try again.")
            return "INVALID"

    def update_levels(self, rankings):
        """Updates team levels based on finishing order."""
        winner = rankings[0]
        winning_team = winner.team

        # Check for game win condition
        if self.teams[winning_team]['level'] == 14: # 'Ace' level
             print(f"\n!!!!!!!!!! TEAM {winning_team} WINS THE GAME !!!!!!!!!!")
             return True

        partner = next(p for p in self.players if p.team == winner.team and p != winner)
        
        partner_rank = rankings.index(partner)
        level_up = 0
        if partner_rank == 1: # 1st and 2nd
            level_up = 3
        elif partner_rank == 2: # 1st and 3rd
            level_up = 2
        elif partner_rank == 3: # 1st and 4th
            level_up = 1

        current_level = self.teams[winning_team]['level']
        new_level = min(current_level + level_up, 14) # Cap level at Ace (14)

        self.teams[winning_team]['level'] = new_level
        print(f"Team {winning_team} goes up by {level_up} levels to Level {self.teams[winning_team]['level']}.")
        
        return False


class SimpleAgent(Player):
    """A basic agent that finds the best valid move it can play."""
    def find_best_play(self, game):
        """Finds the lowest-ranking valid play from its hand."""
        
        possible_plays = []

        # Group cards by value and suit for easy combination generation
        cards_by_value = {}
        for card in self.hand:
            cards_by_value.setdefault(card.value, []).append(card)

        # 1. Generate basic combinations (Singles, Pairs, Triples, Bombs)
        triples = []
        pairs = []
        for value, cards in cards_by_value.items():
            # Singles
            possible_plays.append([cards[0]])
            if len(cards) >= 2:
                pairs.append(cards[0:2])
                possible_plays.append(cards[0:2])
            if len(cards) >= 3:
                triples.append(cards[0:3])
                possible_plays.append(cards[0:3])
            if len(cards) >= 4:
                possible_plays.append(cards)

        # 2. Generate complex combinations
        # Full Houses
        for t in triples:
            for p in pairs:
                if t[0].value != p[0].value:
                    possible_plays.append(t + p)

        # Straights, Tubes, Plates, and Straight Flushes
        unique_values = sorted(cards_by_value.keys())
        for i in range(len(unique_values) - 4):
            # Straights
            if unique_values[i+4] - unique_values[i] == 4:
                straight_cards = [cards_by_value[v][0] for v in unique_values[i:i+5]]
                possible_plays.append(straight_cards)
                # Straight Flushes
                if len(set(c.suit for c in straight_cards)) == 1:
                    possible_plays.append(straight_cards)
        
        # Tubes
        for i in range(len(pairs) - 2):
            p1, p2, p3 = pairs[i], pairs[i+1], pairs[i+2]
            if p2[0].value - p1[0].value == 1 and p3[0].value - p2[0].value == 1:
                possible_plays.append(p1 + p2 + p3)

        # Plates
        for i in range(len(triples) - 1):
            t1, t2 = triples[i], triples[i+1]
            if t2[0].value - t1[0].value == 1:
                possible_plays.append(t1 + t2)

        # Joker Bomb
        jokers = [c for c in self.hand if c.suit == 'Joker']
        if len(jokers) == 2:
            possible_plays.append(jokers)

        # 3. Filter for valid plays and find the best one
        valid_plays = []
        for play in possible_plays:
            # The get_combination_details function is the source of truth for validity
            play_type, rank, _ = game.get_combination_details(play)
            if play_type and game.is_valid_play(play):
                valid_plays.append((rank, play))

        if not valid_plays:
            return [] # Pass

        # Sort by rank and return the lowest-ranking play
        valid_plays.sort(key=lambda x: x[0])
        return valid_plays[0][1]

# --- Main Game Simulation ---
def main():
    player_names = ["Agent 1 (A)", "Agent 2 (B)", "Agent 3 (A)", "Agent 4 (B)"]
    game = GuanDanGame(player_names)
    
    # Replace Player with SimpleAgent
    game.players[0] = SimpleAgent(player_names[0], 'A')
    game.players[1] = SimpleAgent(player_names[1], 'B')
    game.players[2] = SimpleAgent(player_names[2], 'A')
    game.players[3] = SimpleAgent(player_names[3], 'B')
    
    game_over = False
    hand_number = 1
    hand_winner = None

    while not game_over:
        print(f"\n--- Starting Hand {hand_number} ---")
        print(f"Team A is on Level {game.teams['A']['level']}")
        print(f"Team B is on Level {game.teams['B']['level']}")
        
        game.deal()
        
        for p in game.players:
            print(f"{p.name} has {len(p.hand)} cards.")
        
        finish_order = []
        
        if hand_winner:
            game.turn_index = game.players.index(hand_winner)

        while len(finish_order) < 4:
            current_player = game.players[game.turn_index]

            # If player is already out, skip them
            if current_player in finish_order:
                game.turn_index = (game.turn_index + 1) % 4
                continue

            print(f"\nIt's {current_player.name}'s turn. Hand size: {len(current_player.hand)}")
            if game.current_trick:
                 print(f"Current play on table: {[str(c) for c in game.current_trick[-1]]}")

            # Agent makes a move
            play = current_player.find_best_play(game)
            result = game.play_turn(game.turn_index, play)
            
            if result == "HAND_WON":
                print(f"****** {current_player.name} has finished! ******")
                finish_order.append(current_player)
                if len(finish_order) == 1: # First winner
                    game.declarer_team = current_player.team
                    hand_winner = current_player

        print("\n--- Hand Over! ---")
        print("Finishing order:")
        for i, p in enumerate(finish_order):
            print(f"{i+1}. {p.name} (Team {p.team})")
            
        game_over = game.update_levels(finish_order)
        hand_number += 1


if __name__ == "__main__":
    main()
