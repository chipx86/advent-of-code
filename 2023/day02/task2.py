#!/usr/bin/env python3
#
# Now Larry's taking us to fix snow. As one does.
#
# On the way, he decides we need to play another game. Since "I spy with my
# little eye, something that is white and cold" doesn't go over so well I
# guess, we're back to the gosh-dangit cubes.
#
# NOW, he wants to know in each game what the fewest number of cubes of each
# color is possible in a bag. So if we get 3 blue, 4 blue, 19 blue, then the
# fewer is 19, because if we had 14 cubes in the bag, and he pulled out 19,
# he'd be a wizard, and the story doesn't have us dealing with wizard elves
# yet.
#
# Okay so he wants the sum of the power of each game's set of minimums. So,
# the sum total of (min_red * min_green * min_blue) for each game.
#
#
# Approach
# ========
#
# They're giving us another easy one after yesterday. All we have to do is:
#
# 1. Iterate through the lines again.
#
# 2. Iterate through the cubes again (we don't care about the individual
#    hands! It never even mattered! Larry, I swear...)
#
# 3. Store the MAX(prev, new) counts for each cube we match, so we know what
#    the largest number is that we've found for each color.
#
# 4. Multiply the results together and add to the answer.


import re


def get_power_of_minimums():
    line_re = re.compile(r'^Game (?P<id>\d+): (?P<hands>.+)$')
    cube_count_re = re.compile(r'(?P<count>\d+) (?P<color>blue|green|red)')

    answer = 0

    with open('input', 'r') as fp:
        for line in fp:
            m = line_re.match(line)
            assert m

            max_cubes = {
                'red': 0,
                'green': 0,
                'blue': 0,
            }

            for cube_m in cube_count_re.finditer(m.group('hands')):
                count = int(cube_m.group('count'))
                color = cube_m.group('color')

                max_cubes[color] = max(max_cubes[color],
                                       count)

            answer += (max_cubes['red'] *
                       max_cubes['green'] *
                       max_cubes['blue'])

    return answer


answer = get_power_of_minimums()
print(f'Answer = {answer}')
