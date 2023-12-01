#!/usr/bin/env python3
#
# This task involves taking a big list of numbers, going through them in
# order, and shifting over that number by the number itself. One by one,
# until we've gone through all of them. And then we find some numbers at
# certain indexes (wrapping around the list) and adding those numbers together.
#
# The program is really short, really simple.
#
# It did not start that way. I wanted to optimize the hell out of this.
#
# See, Python lists have O(n) complexity for things like inserts and pops.
# Every time we shift, Python has to do a lot of work to shift things around.
# I would never rely on a list in production when wanting to perform these
# sort of operations on this much data.
#
# I didn't want this, and so I thought, hey, let's make a data structure to
# simplify this!
#
# I started working on skip lists, on a B-Tree, but I ultimately decided to
# stop.
#
# Why?
#
# This takes about < 100ms with Python lists. So screw it.
#
# Yeah, it would have made for a more efficient program in theory, but it's
# hard to say if it would have even been worth it. Plus, Python lists are
# implemented in C, and I'm unsure how much additional performance I'd eke out
# by writing such a thing in Python.
#
# You wouldn't believe how much time I spent on this program, though. Just made
# it too difficult for myself.
#
# Oh, one more thing: It turns out there's duplicate numbers in this list.
# I hit problems for a while (hence the time taken) because the values weren't
# adding up. The duplicate lists were the cause. I assumed all values were
# unique. So I altered this to store not just the number, but a pair of
# (original_position, number), which helps make these unique.


with open('input', 'r') as fp:
    # Read each line from the file, storing as (index, num), so we can
    # avoid any issues with duplicate numbers. The actual index value doesn't
    # matter and could be anything unique.
    sequence = [
        (i, int(line))
        for i, line in enumerate(fp.readlines())
    ]

sequence_len = len(sequence)
mod = sequence_len - 1
new_data = list(sequence)

# Run through the sequence, shifting numbers. We'll have positive and
# negative numbers to deal with.
#
# Note that if an item shifts to the end of the list, it'll actually need to
# wrap around to index 0. We take care of this automatically by modding to
# sequence_length - 1. This will cause anything at the last index to become 0.
for i, num in sequence:
    pos = new_data.index((i, num))
    new_pos = (num + pos) % mod

    # While a slow and ineffcient operation in Python, this is fast enough for
    # this task on anything modern.
    #
    # If we wanted to speed this up, we might employ some form of skip list or
    # tree.
    new_data.pop(pos)
    new_data.insert(new_pos, num)

# We can now find our offset used to look up numbers, and get our answer.
start = new_data.index(0)
grove_x = new_data[(start + 1000) % (sequence_len)]
grove_y = new_data[(start + 2000) % (sequence_len)]
grove_z = new_data[(start + 3000) % (sequence_len)]

print('Sum of encrypted coords = %s' % (grove_x + grove_y + grove_z))
