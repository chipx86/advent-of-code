#!/usr/bin/env python3
#
# Day 1, Task 2: https://adventofcode.com/2024/day/1
#
# In part 2, we're calculating a "score" for each location in list 1.
#
# The score is the location's value in list 1 multiplied by the number of
# times it appears in list 2.
#
# This can be done by storing a hashtable/dictionary mapping location IDs to
# hit counts, and a separate list of location IDs, and then iterating through
# those doing the math.
#
# The trick in this input is that we have values in list 2 that aren't in
# list 1, so we can't just work with list 2's items. This requires keeping
# list 1 and iterating through that.

from collections import Counter


def calc_score(
    input_filename: str,
) -> int:
    hits = Counter[int]()
    location_ids1: list[int] = []

    with open(input_filename, 'r') as fp:
        for line in fp:
            parts = line.split('   ')
            assert len(parts) == 2

            location_ids1.append(int(parts[0]))
            hits[int(parts[1])] += 1

    return sum(
        location_id * hits[location_id]
        for location_id in location_ids1
    )


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = calc_score('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 2.
    answer = calc_score('input')
    print(f'Task answer: {answer}')
