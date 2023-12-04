#!/usr/bin/env python3
#
# We went up to a new island in the sky, above the other island in the sky.
# And apparently we suspect that's where water comes from? Sure, why not.
#
# It's called "Island Island." ...
#
# We're supposed to talk to a gardener, but he's on some other island -- the
# surrounded-by-water kind, not the floating-in-the-sky kind, the elf
# clarifies. And if we help him, he'll lend us his boat.
#
# He got scratchcards as a gift, but can't figure out what he's won, implying
# that the lottery system is really defective up there (or working exactly as
# planned).
#
# So we look at the dozens of scratchcards. Each has two lists of
# `|`-separated lists of numbers. The first are the winning numbers, the second
# are numbers the elf has.
#
# We have to figure out which of our numbers are in the winning list.
#
# If there's one match, the card is worth one point. A second doubles it, a
# third doubles that, and so on.
#
#
# Approach
# --------
#
# For each line, we're going to:
#
# 1. Parse the line into sets of numbers.
#
# 2. Get an intersection of the two, which gives us our matches.
#
# 3. If there's a match, we'll bitshift left by NUM - 1.
#
#    So for 2 matches, we'll do 1 << 1, giving us 2 points.
#
#    For 4 matches, we'll do 1 << 3, giving us 8 points.
#
#    And so on. Very simple and fast approach to doing the match. We could
#    also just do 2 ** (NUM - 1) (aka 2 to the power of (NUM - 1)), which gives
#    us the same approach, but I'm opting to do the bitshift because it might
#    be interesting for some people following me to learn.
#
# 4. We'll sum the results.

import re


def get_answer():
    line_re = re.compile(
        r'^Card\s+\d+: (?P<winning_nums>[\d ]+) \| (?P<our_nums>[\d ]+)$')
    answer = 0

    with open('input', 'r') as fp:
        for line in fp:
            m = line_re.match(line)
            assert m

            winning_nums = set(m.group('winning_nums').split())
            our_nums = set(m.group('our_nums').split())

            num_matches = len(winning_nums & our_nums)

            if num_matches > 0:
                answer += (1 << (num_matches - 1))

    return answer


answer = get_answer()
print(f'Answer = {answer}')
