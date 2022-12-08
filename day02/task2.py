#!/usr/bin/env python3
#
# We once again need to find the total score of the hands of
# Rock-Paper-Scissors, as listed in the input. The input will tell us what
# hands the opponent is playing and what hands we should play for that given
# round.
#
# This one differs from task1.py by telling us what hand the opponent is
# playing and what outcome we should aim for (rather than what hand we should
# play).
#
# Like my other solutions, I aim for an optimized approach. That means
# processing one line at a time and keeping minimal state. Just the total
# score.
#
# I keep mappings of inputs to values. Like task1.py, there's a mapping for
# score and moves wins or ties against other moves. There's also a mapping for
# what hands lose against other moves, since we now need to know that in
# order to generate the expected outcome.
#
# There's a final map telling us which map to reference based on which outcome
# we need to generate.
#
# It's then very trivial to take a value from the input, grab the appropriate
# map, play the appropriate hand, and get score.

SCORES = {
    'A': 1,  # Rock
    'B': 2,  # Paper
    'C': 3,  # Scissors
}

LOSES_AGAINST = {
    'A': 'C',  # Rock > Scissors
    'B': 'A',  # Paper > Rock
    'C': 'B',  # Scissors > Paper
}

# Build the inverse of the LOSES_AGAINST map. I could hard-code this, but
# why not.
WINS_AGAINST = {
    _opponent_move: _player_move
    for _player_move, _opponent_move in LOSES_AGAINST.items()
}

TIES_AGAINST = {
    'A': 'A',  # Rock
    'B': 'B',  # Paper
    'C': 'C',  # Scissors
}

WIN_SCORE = 6
TIE_SCORE = 3
LOSE_SCORE = 0


# Map each outcome identifier to the right hands table to play.
OUTCOME = {
    'X': (LOSE_SCORE, LOSES_AGAINST),
    'Y': (TIE_SCORE, TIES_AGAINST),
    'Z': (WIN_SCORE, WINS_AGAINST),
}


total_score = 0

with open('input', 'r') as fp:
    for line in fp:
        assert len(line) == 4

        opponent_move = line[0]
        outcome = line[2]

        score, move_map = OUTCOME[outcome]
        player_move = move_map[opponent_move]
        total_score += score + SCORES[player_move]


print(f'Total score: {total_score}')
