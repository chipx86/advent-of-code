#!/usr/bin/env python3
#
# We need to find the total score of the hands of Rock-Paper-Scissors, as
# listed in the input. The input will tell us what hands the opponent is
# playing and what hands we should play for that given round (win, lose, or
# draw).
#
# Like my other solutions, I aim for an optimized approach. That means
# processing one line at a time and keeping minimal state. Just the total
# score.
#
# I keep mappings of inputs to values, including scores and what hands win
# against or tie against other hands.
#
# It's then trivial to take a value from the input, get a value from the map,
# and make a determination as to the score.

SCORES = {
    'X': 1,  # Rock
    'Y': 2,  # Paper
    'Z': 3,  # Scissors
}

WINS_AGAINST = {
    'X': 'C',  # Rock > Scissors
    'Y': 'A',  # Paper > Rock
    'Z': 'B',  # Scissors > Paper
}

TIES_AGAINST = {
    'X': 'A',  # Rock
    'Y': 'B',  # Paper
    'Z': 'C',  # Scissors
}


WIN_SCORE = 6
TIE_SCORE = 3
LOSE_SCORE = 0


total_score = 0

with open('input', 'r') as fp:
    for line in fp:
        assert len(line) == 4

        opponent_move = line[0]
        player_move = line[2]

        if WINS_AGAINST[player_move] == opponent_move:
            # Player won.
            total_score += WIN_SCORE
        elif TIES_AGAINST[player_move] == opponent_move:
            # Tie.
            total_score += TIE_SCORE
        else:
            # Player lost. No-op.
            total_score += LOSE_SCORE

        total_score += SCORES[player_move]


print(f'Total score: {total_score}')
