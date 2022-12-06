#!/usr/bin/env python3

total_priority = 0

a_ORD = ord('a')
A_ORD = ord('A')

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


if 0:
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
print(ord('r') - a_ORD)
