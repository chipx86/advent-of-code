#!/usr/bin/env python3
#
# Day 2, Task 1: https://adventofcode.com/2024/day/2
#
# In today's task, we're given a list of "reports": lines of a variable
# number of integers. We need to calculate how many reports meet the
# following criteria:
#
# 1. All numbers are in increasing or decreasing order.
# 2. Two adjacent numbers differ by >= 1 and <= 3.
#
# This is pretty straight-forward. For each line in the input:
#
# 1. Normalize the list so that we're comparing in one direction (we'll
#    arbitrarily pick a decreasing list), based on the first two values.
#
# 2. Run through the items and compare them.

def calc_safe_reports(
    filename: str,
) -> int:
    answer: int = 0

    with open(filename, 'r') as fp:
        for line in fp:
            levels = [
                int(value)
                for value in line.split(' ')
            ]

            valid: bool = True

            # We're going to start with a simple test: Which direction does
            # the list seem to be going? We'll compare the first two numbers
            # and then check the rest from there. This gives us a start for
            # how we want to compare values.
            #
            # We don't want to duplicate a lot of code, so we're going to
            # reverse the list in one case and reuse logic.
            if levels[0] < levels[1]:
                levels = levels[::-1]

            # Now we can run through and test.
            prev_level = levels[0]

            for level in levels[1:]:
                if not (prev_level > level and
                        1 <= prev_level - level <= 3):
                    valid = False
                    break

                prev_level = level

            if valid:
                answer += 1

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = calc_safe_reports('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = calc_safe_reports('input')
    print(f'Task answer: {answer}')
