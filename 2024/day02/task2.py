#!/usr/bin/env python3
#
# Day 2, Task 2: https://adventofcode.com/2024/day/2
#
# They forgot to tell us about the Problem Dampener! This lets the reactor
# tolerate a single bad level in an otherwise-safe report. Good. Safe.
# Excellent.
#
# So we need to update our logic to allow tolerance of a single error.
# The trick here is that we may encounter an error in the middle of a report,
# the start of the report, or the end of the report.
#
# We can no longer assume an order or type of error. We have to track where
# errors occur and check variations without possible errored items.

from typing import Optional


def check_report(
    report: list[int],
) -> Optional[int]:
    prev_level = report[0]

    for i, level in enumerate(report[1:], start=1):
        if not (prev_level > level and
                1 <= prev_level - level <= 3):
            return i

        prev_level = level

    return None


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

            # We need to be more tolerant of problems, so we can't assume
            # things like the initial order or type of failure.
            #
            # What we'll do instead is build up some starting candidates:
            #
            # 1. The list in provided order.
            # 2. The list in sorted order.
            #
            # Then we'll check the report.
            #
            # If it's valid, we're done!
            #
            # If it's not valid, we'll try up to two more times, removing
            # either the error position or the position preceding it. Both
            # may be invalid, so we need to try separately without them.
            #
            # If we get a valid result, we're good.
            candidates = [levels, levels[::-1]]

            for candidate in candidates:
                # Now we can run through and test.
                error_pos = check_report(candidate)

                if error_pos is None:
                    valid = True
                else:
                    valid = (
                        # Check while skipping this position.
                        check_report(candidate[:error_pos] +
                                     candidate[error_pos + 1:]) is None or

                        # Check while skipping the previous position.
                        check_report(candidate[:error_pos - 1] +
                                     candidate[error_pos:]) is None
                    )

                if valid:
                    answer += 1
                    break

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = calc_safe_reports('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 1.
    answer = calc_safe_reports('input')
    print(f'Task answer: {answer}')
