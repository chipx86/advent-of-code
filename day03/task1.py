#!/usr/bin/env python3

total_priority = 0

a_ORD = ord('a')
A_ORD = ord('A')

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
