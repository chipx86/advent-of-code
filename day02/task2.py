#!/usr/bin/env python3

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
