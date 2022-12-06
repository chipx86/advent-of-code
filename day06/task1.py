#!/usr/bin/env python3

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
