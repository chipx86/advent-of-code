#!/usr/bin/env python3
#
# We need to find the elf that's carrying the most calories, and what that
# total number is.
#
# I'm aiming to keep memory usage at a minimum, so I'm processing each line
# at a time and then moving on, keeping as little state as possible.
#
# We know that subsequent lines without a blank line all represent calorie
# counts for the same elf, so I'm taking advantage of that by keeping a running
# total of calories that's reset when a blank line is encountered.
#
# The maximum calorie count (and the associated elf) are tracked as global
# state. There's also a "current elf" total. Every time we process a line, we
# add to the current elf's calorie total, and at any point that that exceeds
# the global maximum (which may be multiple times for a given elf), we update
# that value.
#
# This is just a bit easier than having to gather a total and wait for a blank
# line, because I don't have to add a condition to compute this at the end of
# input processing. So it's just a bit easier to manage, and just a bit more
# resilient.

cur_elf = 1
cur_elf_calories = 0
max_elf = 0
max_elf_calories = 0


with open('input', 'r') as fp:
    for line in fp:
        line = line.strip()

        if line:
            cur_elf_calories += int(line)

            if cur_elf_calories > max_elf_calories:
                max_elf_calories = cur_elf_calories
                max_elf = cur_elf
        else:
            cur_elf += 1
            cur_elf_calories = 0


print('Elf %s: Max calories: %s' % (max_elf, max_elf_calories))
