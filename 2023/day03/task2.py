#!/usr/bin/env python3
#
# Oh good, we found that part. Math wins again.
#
# Oh by the way, Carl is a woman. Thanks, part 2. Henceforth, she will be
# known as Carla.
#
# Turns out Carla installed the missing part, but installed the wrong gear.
#
# Gears are represented by `*` symbols, which seems about right. But only when
# they're adjacent to *exactly* two part numbers. Multiply note numbers
# together and we get a "gear ratio."
#
# So now we need to find every gear ratio and add them all up.
#
#
# Approach
# --------
#
# Our old approach is going to work fine. However, we'll now only consider
# numbers adjacent to a `*`.
#
# Since we have to track both numbers, we're also going to store a map of
# gear positions to lists of numbers. When we find gears, we'll place the
# coordinates of the gear in this map, associating it with the number that was
# being processed.
#
# Because I'm tired and don't have a lot of time, I'm going to store a global
# map that spans the whole file, but room for improvement here would be to
# process and then discard anything gears on any lines going out of scope.
# Maybe later.


# This function is the same as in task1. It's documented here exactly the
# same as before for convenience.
def scan_lines(fp):
    # So there's a few ways we could do this. We could manage a group of 3
    # lines in a list, or in a deque (which will be faster), or we can just
    # track these as a variable per line.
    #
    # I want to be able to indicate to the caller which line is the scanning
    # line, and this will change as we exhaust the lines of the file, so I'm
    # going with separate state lines because that's easiest.
    #
    # We're going to be reading into `post_line`, then as we go we'll rotate
    # that up to `scan_line`, then `pre_line`.
    #
    # We start by populating post_line.
    #
    # Note that our lines will intentitonally retain the newline symbols, for
    # reasons I go into below.
    pre_line = None
    scan_line = None
    post_line = fp.readline()

    # Now, in reality, these three lines will be populated. But if we couldn't
    # trust the input to be of a certain minimum length, we'd still be covered,
    # as we'll bail below.
    #
    # This loop will go until we have nothing left in the file.
    while post_line:
        # We'll move everything up one.
        pre_line = scan_line
        scan_line = post_line
        post_line = fp.readline()

        yield pre_line, scan_line, post_line

        # If post_line was empty, then we're going to be exiting the loop
        # shortly. We also know that scan_line at this point will have been
        # the last line of the file. So we'd be done! Nice and clean.
        #
        # If there's more to read, then we naturally continue reading.


# This is mostly the same as in task1.py, but we're also providing the row
# offset from pre_line.
def get_search_space(*, pre_line, scan_line, post_line, pos, first_digit):
    # Note that because of the newline at the end of the lines, we don't have
    # to worry about boundary issues on the right-hand side.
    if pre_line:
        # North-East
        yield pre_line, 0, pos + 1

        # North
        yield pre_line, 0, pos

        if pos > 0:
            # North-West
            yield pre_line, 0, pos - 1

    if first_digit and pos > 0:
        # West
        yield scan_line, 1, pos - 1

    # East
    yield scan_line, 1, pos + 1

    if post_line:
        # South-East
        yield post_line, 2, pos + 1

        # South
        yield post_line, 2, pos

        if pos > 0:
            # South-West
            yield post_line, 2, pos - 1


def get_answer():
    answer = 0
    gear_map = {}

    with open('input', 'r') as fp:
        for row, (pre_line, scan_line, post_line) in enumerate(scan_lines(fp)):
            # Work our way through the line, looking for numbers.
            num_buffer = ''
            symbol_keys = []

            # Note that the lines we're working with have a newline at the
            # end. This is a good thing! While this won't be a symbol, it
            # will trigger the end of number processing and calculating the
            # result for the number buffer.
            #
            # There are some differences between this implementation and
            # task1.py.
            #
            # 1. We're no longer going to bail out of searching when we find
            #    a "*" (it's possible it'll be adjance to multiple gears that
            #    need to be considered
            #
            # 2. We'll store a map of numbers.
            for pos, c in enumerate(scan_line):
                if c.isdigit():
                    # This is a part number.
                    num_buffer += c

                    search = get_search_space(
                        pre_line=pre_line,
                        scan_line=scan_line,
                        post_line=post_line,
                        pos=pos,
                        first_digit=(len(num_buffer) == 1))

                    for search_line, row_offset, pos in search:
                        search_c = search_line[pos]

                        if search_c == '*':
                            # We found a gear. Record its position for
                            # resolving once we're done with processing the
                            # number.
                            symbol_keys.append((row + row_offset, pos))
                else:
                    if symbol_keys:
                        num = int(num_buffer)

                        # Note that we can have duplicates above. Multiple
                        # digits may map to the same gear. So, we de-duplicate
                        # by converting to a set here.
                        for symbol_key in set(symbol_keys):
                            gear_map.setdefault(symbol_key, []).append(num)

                        symbol_keys = []

                    num_buffer = ''

    # This little expression loops through all gears with exactly two numbers,
    # multiplies them together, and includes in the sum.
    answer = sum(
        int(nums[0]) * int(nums[1])
        for nums in gear_map.values()
        if len(nums) == 2
    )

    return answer


answer = get_answer()
print(f'Answer = {answer}')
