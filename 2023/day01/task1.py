#!/usr/bin/env python3
#
# https://adventofcode.com/2023/day/1
#
# Oh no, something's up with snow production! We gotta fix the snow machine!
# This requires calibration, and our puzzle input contains the calibration
# instructions. But some elf amended it and now the other elves are having
# trouble reading it.
#
# In the puzzle input, each line of text originally contained a calibration
# value. To get this, we need to combine the first digit and then the last
# digit to form a two-digit number. So, '1abc9' is 19.
#
# Oh, but not all lines have two digits! If it only has one, then we use it
# as the first and last digit.
#
# The final answer is the sum of all the combined numbers.
#
# The puzzle input has 1000 lines. We want to be efficient, since, hey, this
# could have millions!
#
# Reading through each line is easy. As for determining the integers, we have
# a few methods we could try:
#
# 1. Strip out all the non-number values from the string and grab the
#    remaning first character and last character.
#
#    This is far from optimal. We'd be transforming strings, which isn't
#    "fast".
#
# 2. Generate a regex to grab the numbers, ignoring anything else.
#
#    This could be okay. Regexes are somewhat fast if done well enough. They're
#    native code, which helps. But it's not actually as fast as we'd prefer.
#
# 3. Loop through the starting characters until we find a number, then loop
#    backwards through the ending characters until we find a number.
#
#    This is actually the fastest. This can be verified by running each
#    approach 1000 times and seeing how long they take (which we'll do!).

import re
import timeit


# The more optimal character iteration approach.
def iter_chars_approach():
    total = 0

    with open('input', 'r') as fp:
        for line in fp:
            digit1 = None
            digit2 = None

            # We'll walk each direction across the line, looking for a
            # character that is between '0' and '9'. We'll then combine those,
            # convert to an integer, and add to the running total.
            for c in line:
                if '0' <= c <= '9':
                    digit1 = c
                    break

            for c in reversed(line):
                if '0' <= c <= '9':
                    digit2 = c
                    break

            assert digit1 is not None
            assert digit2 is not None

            total += int(digit1 + digit2)

    return total


# The regex approach.
def regex_approach():
    values_re = re.compile(r'^[^\d]*(\d).*?(\d)?[^\d]*$')
    total = 0

    with open('input', 'r') as fp:
        for line in fp:
            m = values_re.match(line)
            assert m, line

            # For matches with only a single digit, we'll get that digit in
            # group 1, but a None in group 2. So we'll need to fall back.
            # Note that these are strings, so there's no risk of '0' being
            # falsy.
            digit1 = m.group(1)
            digit2 = m.group(2) or digit1

            total += int(digit1 + digit2)

    return total


# We'll make sure we get the same value with either approach.
answer1 = iter_chars_approach()
answer2 = regex_approach()

assert answer1 == answer2

print(f'Answer: {answer1}')


# We can time our approaches:
print()
print('Iterate characters approach:',
      timeit.timeit(iter_chars_approach, number=1000))
print('Regex approach:',
      timeit.timeit(regex_approach, number=1000))
