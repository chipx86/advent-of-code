#!/usr/bin/env python3

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
