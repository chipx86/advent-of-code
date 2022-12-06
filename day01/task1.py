#!/usr/bin/env python3

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
