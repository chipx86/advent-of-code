#!/usr/bin/env python3
#
# This is the same as task 1, but we're multiplying each value by the
# decryption key.
#
# Also, we're running the mixing 10 times.
#
# Now this has a notable difference in behavior from task 1. In task 1,
# we knew we were only mixing the list once, so once we put an item somewhere,
# we never had to refer to it again. This allowed us to go from storing a
# pair of (i, num), which I describe in task1.py, to simply storing num.
#
# We can't do that here, because we have to refer to each number 10 times.
#
# So now we store (i, num) each time. Which is fine. The only implication
# for this is that we can no longer look for 0 anymore. We have to look for
# the (i, 0) item. So we simply store where this is up-front when reading
# the lines.
#
# Pretty straight-forward addition to task1.py.


DECRYPTION_KEY = 811589153


zero = None
sequence = []

with open('input', 'r') as fp:
    # Read each line from the file, storing as (index, num), so we can
    # avoid any issues with duplicate numbers. The actual index value doesn't
    # matter and could be anything unique.
    #
    # We're multiplying each stored number with our decryption key. This
    # doesn't really affect anything in this implementation, but could affect
    # implementations that assume numbers can be used as indexes into
    # something. It also would impact the amount of positions something would
    # need to shift, but we divide and use the remainder to generate our
    # destination position.
    #
    # Also, we store the location of the '0' item, so we can look it up after.
    # We didn't have to do this in task1.py, because our resulting list was
    # just numbers, not (i, num).
    for i, line in enumerate(fp.readlines()):
        num = int(line) * DECRYPTION_KEY
        item = (i, num)

        sequence.append(item)

        if num == 0:
            zero = item

sequence_len = len(sequence)
mod = sequence_len - 1
new_data = list(sequence)

# Run through the sequence 10 times, shifting numbers. We'll have positive and
# negative numbers to deal with.
#
# Note that if an item shifts to the end of the list, it'll actually need to
# wrap around to index 0. We take care of this automatically by modding to
# sequence_length - 1. This will cause anything at the last index to become 0.
for n in range(10):
    for i, num in sequence:
        pos = new_data.index((i, num))
        new_pos = (num + pos) % mod

        # While a slow and ineffcient operation in Python, this is fast enough
        # for this task on anything modern.
        #
        # If we wanted to speed this up, we might employ some form of skip list
        # or tree.
        new_data.pop(pos)
        new_data.insert(new_pos, (i, num))

# We can now find our offset used to look up numbers, and get our answer.
start = new_data.index(zero)
grove_x = new_data[(start + 1000) % (sequence_len)][1]
grove_y = new_data[(start + 2000) % (sequence_len)][1]
grove_z = new_data[(start + 3000) % (sequence_len)][1]

print('Sum of encrypted coords = %s' % (grove_x + grove_y + grove_z))
