#!/usr/bin/env python3
#
# Oh silly us. The card listed the rules and we were just bad at reading.
#
# Sounds about right.
#
# There are no points! We made it up! No wonder nobody gives us our winnings...
# Instead, the number of matching numbers == more new scratchcards.
#
# Kinda. So, the idea is that:
#
# 1. If you win X numbers on a card, you'll win X new cards with card numbers
#    satrting at WINNING_CARD_NUM + 1.
#
# 2. If a card that was won also has a winning number on it, then the cards
#    it wins will have card numbers starting at the original card's
#    WINNING_CARD_NUM + 1.
#
#    Yeah this is confusing. So there are *copies* of cards. You can have,
#    say, 4 copies of Card 42. And these are copies. If Card 42 won 3, then
#    any copy will win 3.
#
#    There will never be more won cards than the total number of cards in the
#    game.
#
# 3. We'll track the total number of original and won scratchcards. That total
#    is the answer.
#
#
# Approach
# --------
#
# We're going to keep a multiplier map, going from card number to a multiplier
# integer. We'll keep this minimal, discarding the previous line's entry as we
# iterate through lines, in order to minimize memory consumption.
#
# For each line, we're going to:
#
# 1. Parse the line into sets of numbers, and giving us the ID.
#
# 2. Discard any multipliers from previous entries, to save memory.
#
# 3. Figure out if we have a multiplier for this line. We'll add 1 to this and
#    add that to our total (the answer). This is the number of duplicate cards
#    previously won for this card number.
#
# 4. Once again, get an intersection of the two, which gives us our matches.
#
# 5. If there's a match, populate the multipliers with the new cards (adding
#    if there's already existing ones there).

import re
from collections import defaultdict


def get_answer():
    line_re = re.compile(
        r'^Card\s+(?P<card_num>\d+): '
        r'(?P<winning_nums>[\d ]+) \| '
        r'(?P<our_nums>[\d ]+)$'
    )

    total_cards = 0
    card_multipliers = defaultdict(int)

    with open('input', 'r') as fp:
        for line in fp:
            m = line_re.match(line)
            assert m

            card_num = int(m.group('card_num'))

            # Clear out any prior tracking for previous lines that we'll never
            # again update.
            card_multipliers.pop(card_num - 1, None)

            # Add at least one card to the total. If there's a multiplier,
            # we'll add those cards plus this one.
            multiplier = card_multipliers.get(card_num, 0) + 1
            total_cards += multiplier

            winning_nums = set(m.group('winning_nums').split())
            our_nums = set(m.group('our_nums').split())

            num_matches = len(winning_nums & our_nums)

            if num_matches > 0:
                # Populate the card multipliers with any cards we just won.
                #
                # Note the + 1 at the end. This is because range() takes the
                # upper bound as exclusive rather than inclusive. We want the
                # value of card_num + num_matches to be in the result.
                for i in range(card_num + 1, card_num + num_matches + 1):
                    card_multipliers[i] += multiplier

    return total_cards


answer = get_answer()
print(f'Answer = {answer}')
