#!/usr/bin/env python3
#
# Day 5, Task 2: https://adventofcode.com/2024/day/5
#
# This is pretty similar to task 1. The ONLY difference is that we only want
# to look at pages that were NOT in the right order. The only change between
# this and task 1 is a change from `==` to `!=`. Easy!

import functools
from collections import defaultdict


def printer_fiasco(
    filename: str,
) -> int:
    answer: int = 0
    order_map: dict[int, set[int]] = defaultdict(set)
    in_order_map: bool = True

    # Define our custom sort function. We'll sort based on the mapping.
    def order_map_cmp(
        a: int,
        b: int,
    ) -> int:
        if b in order_map.get(a, set()):
            return -1
        elif a in order_map.get(b, set()):
            return 1
        else:
            return 0

    # Parse the input.
    with open(filename, 'r') as fp:
        for line in fp:
            line = line.strip()

            if not line:
                # We've hit the divider between page order mapping and
                # lists of pages.
                in_order_map = False
                continue

            if in_order_map:
                # Store which pages come before which other pages.
                parts = line.split('|')
                assert len(parts) == 2

                a = int(parts[0])
                b = int(parts[1])
                order_map[a].add(b)
            else:
                # We're processing a set of pages. We just need to sort the
                # pages with our custom sort function and then see if it's
                # different from the original list of pages.
                pages = [
                    int(page)
                    for page in line.split(',')
                ]

                sorted_pages = sorted(pages,
                                      key=functools.cmp_to_key(order_map_cmp))

                # The only change made from task1 is inverting this
                # conditional. Same sort logic. We just want to look at the
                # incorrectly-ordered lines.
                if pages != sorted_pages:
                    # This list of pages was already in the right order.
                    # Grab the middle item and add to the answer.
                    assert len(sorted_pages) % 2 == 1

                    middle_page = sorted_pages[len(sorted_pages) // 2]
                    answer += middle_page

    return answer


if __name__ == '__main__':
    # First, let's verify our sample's answer.
    answer = printer_fiasco('sample-input')
    print(f'Sample answer: {answer}')

    # Now do task 2.
    answer = printer_fiasco('input')
    print(f'Task answer: {answer}')
