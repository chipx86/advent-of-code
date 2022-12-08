#!/usr/bin/env python3
#
# We now need to process three lines of rucksacks at a time and find the
# duplicate items, then calculate the sum of priorities.
#
# This is similar to task1.py, but we're now reading three lines up-front,
# and converting each to a set.
#
# Python's set() data type makes this logic very simple. I can convert the
# values in each compartment (which are just [A-Za-z]) to a set(), and then
# get the intersection of two sets to figure out where the duplicate is. This
# is probably the fastest approach in Python, since this utilizes C code for
# this handling.
#
# Then I calculate a priority based on uppercase or lowercase letters. There
# are many was this could be done, but I go with simple math. We can easily
# compare letters for ranges, to see if it's uppercase or lowercase (we could
# also use some string functions for this).
#
# To actually calculate a priority, we're getting the character codes and
# calculating based on the lowest in the range ('a' or 'A'). This gives us an
# index into the alphabet that we can add on to a starting priority value.

a_ORD = ord('a')
A_ORD = ord('A')


total_priority = 0

with open('input', 'r') as fp:
    while True:
        rucksack1 = fp.readline().strip()

        if not rucksack1:
            # We're done.
            break

        rucksack2 = fp.readline().strip()
        rucksack3 = fp.readline().strip()

        assert rucksack2
        assert rucksack3

        common_items = set(rucksack1) & set(rucksack2) & set(rucksack3)
        assert len(common_items) == 1

        item = list(common_items)[0]

        if 'a' <= item <= 'z':
            total_priority += 1 + (ord(item) - a_ORD)
        elif 'A' <= item <= 'Z':
            total_priority += 27 + (ord(item) - A_ORD)

print(f'Total priority = {total_priority}')
