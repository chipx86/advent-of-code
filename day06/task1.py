#!/usr/bin/env python3
#
# We need to find out how many characters it takes to get to the tootsie
# roll center of a tootsie pop.
#
# I mean, how many characters until we've processed start of input through
# end of a marker. The marker is a sequence of 4 bytes that don't repeat
# (all unique).
#
# This is easy in Python, because we have set()! Like my other solutions, I
# am for memory and performance optimization.
#
# All I need to do is read a byte at a time from the file, keeping track of
# how many bytes I've read, and storing the most recent 4 bytes (marker size).
# Each iteration, I can convert the marker candidate buffer to a set(), and
# then check the length. If it's the marker size, we know all 4 characters
# are unique, and we know how many bytes we've read, so we're done!

MARKER_LEN = 4


with open('input', 'r') as fp:
    count = 0
    buf = []

    while len(set(buf)) != MARKER_LEN:
        count += 1
        c = fp.read(1)

        if not c:
            break

        buf = buf[-(MARKER_LEN - 1):] + [c]


print('code = %r' % ''.join(buf))
print('count = %s' % count)
