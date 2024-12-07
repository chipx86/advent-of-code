#!/usr/bin/env python3
#
# Day 7, Task 1: https://adventofcode.com/2024/day/7
#
# This task is about trying to solve equations when we only have the numbers.
# We know the answer, we know the values going into the equation, but we
# don't know the operators. So we have to try them.
#
# We're limited in task 1 to addition and multiplication operators. We want
# to try each combination, but we don't want to do so naively. We want to,
# say, only try to multiply the same two numbers once for any given operator,
# rather than doing it more than once.
#
# So our approach is a recursive generator that calculates the value for a
# pair of numbers for each possible operator, then calculates the result of
# that with the next number using each possible operator, and so on.
#
# Pretty easy. Pretty fast.

import operator
from typing import Iterator


def calc(
    *,
    nums: list[int],
    value: int,
    num_i: int = 1,
) -> Iterator[int]:
    if len(nums) == num_i:
        yield value
        return

    b = nums[num_i]
    num_i += 1

    for op in (operator.add, operator.mul):
        yield from calc(nums=nums,
                        num_i=num_i,
                        value=op(value, b))


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
                                    value=nums[0]):
                if calc_answer == expected_line_answer:
                    answer += calc_answer
                    break

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = missing_op_calc('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = missing_op_calc('input')
    print(f'Task answer: {answer}')
