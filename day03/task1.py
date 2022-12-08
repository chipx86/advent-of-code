#!/usr/bin/env python3
#
# We need to look in both compartments of each rucksack, looking for a
# duplicate item, and then getting the sum of priorities for each.
#
# For this, like many others, I take an optimized approach. Process one line
# at a time, keep minimal state.
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
    for line in fp:
        line = line.strip()
        num_compartment_items = len(line) // 2
        compartment1 = line[:num_compartment_items]
        compartment2 = line[num_compartment_items:]

        for item in set(compartment1) & set(compartment2):
            if 'a' <= item <= 'z':
                total_priority += 1 + (ord(item) - a_ORD)
            elif 'A' <= item <= 'Z':
                total_priority += 27 + (ord(item) - A_ORD)

print(f'Total priority = {total_priority}')
