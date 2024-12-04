#!/usr/bin/env python3
#
# Day 3, Task 1: https://adventofcode.com/2024/day/3
#
# Ah, our first introduction to instruction processing. This came sooner
# than I expected.
#
# We have program code consisting of mul(X,Y) instructions, where X and Y
# are 1-3 digit integers. We need to execute those and add the result to our
# answer.
#
# But there's a catch! The program code is corrupted. Garbled. Written by a
# really awful AI, maybe. So we need to ignore anything that is not an
# instruction, and execute anything that is.
#
# Sounds safe. No security risks there.
#
# Obviously this is about to get more complex, but as a simple demonstration
# of regexes, let's iterate through all the self-contained mul(X,Y)
# instructions we can find on each line and process them.

import re


MUL_RE = re.compile(r'mul\((\d{1,3}),(\d{1,3})\)')


def safely_run_muls(
    filename: str,
) -> int:
    answer: int = 0

    with open(filename, 'r') as fp:
        for line in fp:
            for m in MUL_RE.finditer(line):
                # We know these are integers, since we matched against \d,
                # so no need to be careful about deserializing.
                answer += int(m.group(1)) * int(m.group(2))

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = safely_run_muls('sample-input1')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = safely_run_muls('input')
    print(f'Task answer: {answer}')
