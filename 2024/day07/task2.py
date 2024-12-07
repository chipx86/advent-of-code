#!/usr/bin/env python3
#
# Day 7, Task 2: https://adventofcode.com/2024/day/7
#
# Task 2 iterates on task 1 with one new operator: A concatenation operator.
#
# This is easy to implement. We just f-string the numbers and convert to an
# integer. This isn't free, and the addition of a new operator means we're
# doing a lot more calculations than before. This adds a more noticeable
# runtime (it was just around 6.5 seconds here).
#
# I wanted to bring that down, so I added a limit. If we pass the limit during
# any equation, we just bail. No point in doing any more work. This takes it
# to 3.8 seconds here.

import operator
from typing import Iterator


def concat_op(
    a: int,
    b: int,
) -> int:
    return int(f'{a}{b}')


def calc(
    *,
    nums: list[int],
    value: int,
    limit: int,
    num_i: int = 1,
) -> Iterator[int]:
    if len(nums) == num_i:
        yield value
        return

    b = nums[num_i]
    num_i += 1

    for op in (operator.add, operator.mul, concat_op):
        op_answer = op(value, b)

        if op_answer <= limit:
            yield from calc(nums=nums,
                            num_i=num_i,
                            limit=limit,
                            value=op_answer)


def missing_op_calc(
    filename: str,
) -> int:
    answer: int = 0

    with open(filename, 'r') as fp:
        for line in fp:
            parts = line.split()
            expected_line_answer = int(parts[0][:-1])
            nums = [
                int(item)
                for item in parts[1:]
            ]

            for calc_answer in calc(nums=nums,
                                    value=nums[0],
                                    limit=expected_line_answer):
                if calc_answer == expected_line_answer:
                    answer += calc_answer
                    break

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = missing_op_calc('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 2.
    answer = missing_op_calc('input')
    print(f'Task answer: {answer}')
