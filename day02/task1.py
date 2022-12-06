#!/usr/bin/env python3

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
