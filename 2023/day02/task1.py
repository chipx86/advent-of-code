#!/usr/bin/env python3
#
# So we got shot into the sky and ended up on a large island. As you do.
# This place is called Snow Island, and the Elf there has some colored cube
# fascination. Probably a 4/8 year employment anniversary gift. He doesn't
# have a name, so I'm calling him Larry.
#
# Anyway, they're in a bag, and we don't know how many there are. Each time
# we play his cubes-in-a-bag guessing game, the numbers are different.
#
# Here's how the game works:
#
# 1. Larry puts a secret number of each type of cube in a bag.
# 2. Several times per game, Larry will reach into the bag, grab a random
#    handful of cubes, show them, and then put them back in.
#
# Fun.
#
# Several games are played, and the recordings of each handful of cubes are
# recorded as puzzle input.
#
# Larry wants to know which of the played games could still have been
# possible if the bag only had 12 red cubes, 13 green cubes, 14 blue cubes.
#
# We take the IDs of each game that could have been played (this is also in
# the puzzle input) and sum them as the answer.
#
#
# Approach
# ========
#
# 1. We're going to go through each line, using a regex to incrementally
#    iterate through each cube count.
#
#    For this task, we don't care about the hands. We only need to make sure
#    no individual group of cubes of a given color exceed Larry's limits.
#
# 2. As soon as we find a number on a given line that exceeds a limit, we
#    bail on that game.
#
#    There's no need further process the remaining cubes if we've exceeded
#    a limit.
#
# 3. If the game is possible, we add the numeric ID to the answer.

import re


def get_sum_possible_games():
    line_re = re.compile(r'^Game (?P<id>\d+): (?P<hands>.+)$')
    cube_count_re = re.compile(r'(?P<count>\d+) (?P<color>blue|green|red)')

    cube_limits = {
        'red': 12,
        'green': 13,
        'blue': 14,
    }

    answer = 0

    with open('input', 'r') as fp:
        for line in fp:
            m = line_re.match(line)
            assert m

            possible_game = True

            for cube_m in cube_count_re.finditer(m.group('hands')):
                count = int(cube_m.group('count'))
                color = cube_m.group('color')

                if count > cube_limits[color]:
                    possible_game = False
                    break

            if possible_game:
                answer += int(m.group('id'))

    return answer


answer = get_sum_possible_games()
print(f'Answer = {answer}')
