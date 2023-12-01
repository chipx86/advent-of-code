#!/usr/bin/env python3
#
# We need to find the top three elves carrying the most calories, and what
# that total is for all three.
#
# This works differently from task1.py. I now need to gather the totals for
# a given elf before processing it, unlike in that task where I could process
# line-by-line.
#
# So we have one function that handles iteration, and counting of calories for
# an elf. It yields data any time we know we're done processing for a given
# elf, whether due to a blank line or end-of-file.
#
# That then lets us keep our processing loop simple. We just iterate over the
# data yielded.
#
# We still need to know the top three elves and their calories, so what we do
# is keep a list of the top 3, in order from highest to lowest calories.
# For each result, we loop through the rankings and see if the new elf beats
# out a ranked elf to a calorie count. If so, we insert the new one right
# before that one, and then we cap the ranks back to 3.


TOP_RANKED_ELVES = 3

# These are ranked from highest to lowest calorie counts.
#
# Tuple of: (elf_num, calories)
max_elf_rankings = [(0, 0)] * TOP_RANKED_ELVES


def iter_elf_input():
    found_calories = False
    elf = 1
    calories = 0

    with open('input', 'r') as fp:
        for line in fp:
            line = line.strip()

            if line:
                calories += int(line)
                found_calories = True
            elif found_calories:
                yield elf, calories
                elf += 1
                calories = 0
                found_calories = False

        if found_calories:
            yield elf, calories


for cur_elf, cur_calories in iter_elf_input():
    for i, (max_elf, max_calories) in enumerate(max_elf_rankings):
        if cur_calories >= max_calories:
            max_elf_rankings.insert(i, (cur_elf, cur_calories))
            max_elf_rankings = max_elf_rankings[:3]
            break


print('Rankings:')

total_max_calories = 0

for max_elf, max_calories in max_elf_rankings:
    print('Elf %s: %s' % (max_elf, max_calories))

    total_max_calories += max_calories

print()
print('Total max calories = %s' % total_max_calories)
