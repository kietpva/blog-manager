from copy import deepcopy


# Exercise 17.12.2
class Deck:
    def __init__(self, cards=None):
        self.cards = cards or []

    def __str__(self):
        return "\n".join(str(card) for card in self.cards)


class Card:
    suit_names = ["Clubs", "Diamonds", "Hearts", "Spades"]
    rank_names = (
        [None, "Ace"] + [str(n) for n in range(2, 11)] + ["Jack", "Queen", "King"]
    )

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank_names[self.rank]} of {self.suit_names[self.suit]}"


class Trick(Deck):
    """Represents a trick in contract bridge."""

    def find_winner(self):
        led_suit = self.cards[0].suit
        winning_index = 0
        winning_card = self.cards[0]

        for i, card in enumerate(self.cards):
            if card.suit == led_suit and card.rank > winning_card.rank:
                winning_card = card
                winning_index = i

        return winning_index


cards = [
    Card(1, 3),  # 3 of Diamonds
    Card(1, 10),  # 10 of Diamonds
    Card(1, 12),  # Queen of Diamonds
    Card(2, 13),  # King of Hearts
]

trick = Trick(cards)
print(trick.find_winner())


# Exercise 17.12.4
class Hand(Deck):
    """Represents a hand of playing cards."""

    pass


class PokerHand(Hand):
    """Represents a poker hand."""

    def get_suit_counts(self):
        counter = {}
        for card in self.cards:
            counter[card.suit] = counter.get(card.suit, 0) + 1
        return counter

    def get_rank_counts(self):
        counter = {}
        for card in self.cards:
            counter[card.rank] = counter.get(card.rank, 0) + 1
        return counter

    def has_straight(self):
        ranks = list(self.get_rank_counts().keys())

        # Ace can be high
        if 1 in ranks:
            ranks.append(14)

        ranks.sort()

        count = 1
        for i in range(1, len(ranks)):
            if ranks[i] == ranks[i - 1] + 1:
                count += 1
                if count >= 5:
                    return True
            else:
                count = 1

        return False

    def has_straight_flush(self):
        suit_counts = self.get_suit_counts()

        for suit, count in suit_counts.items():
            if count < 5:
                continue

            suited_cards = [card for card in self.cards if card.suit == suit]

            suited_hand = PokerHand(suited_cards)

            if suited_hand.has_straight():
                return True

        return False

    def has_pair(self):
        rank_counts = self.get_rank_counts()

        for count in rank_counts.values():
            if count >= 2:
                return True

        return False

    def has_full_house(self):
        rank_counts = self.get_rank_counts()

        has_three = False
        has_two = False

        for count in rank_counts.values():
            if count == 3:
                has_three = True
            elif count == 2:
                has_two = True

        return has_three and has_two


cards = [
    Card(0, 13),  # King
    Card(1, 1),  # Ace
    Card(2, 2),
    Card(3, 3),
    Card(0, 4),
]

hand = PokerHand(cards)
print("Has straight?", hand.has_straight())

# Exercise 17.12.5
cards = [
    Card(2, 5),
    Card(2, 6),
    Card(2, 7),
    Card(2, 8),
    Card(2, 9),
    Card(1, 13),
    Card(0, 3),
]

hand = PokerHand(cards)
print("Has straight flush?", hand.has_straight_flush())

# Exercise 17.12.6
bad_hand = PokerHand(
    [
        Card(0, 2),  # 2 of Clubs
        Card(0, 3),  # 3 of Clubs
        Card(2, 4),  # 4 of Hearts
        Card(3, 5),  # 5 of Spades
        Card(0, 7),  # 7 of Clubs
    ]
)

pair = deepcopy(bad_hand)
pair.cards.append(Card(1, 2))  # 2 of Diamonds

print(pair)
print(pair.has_pair())

print(bad_hand.has_pair())

# Exercise 17.12.7
full_house = PokerHand(
    [
        Card(0, 3),
        Card(1, 3),
        Card(2, 3),
        Card(0, 7),
        Card(1, 7),
    ]
)

print(full_house.has_full_house())
