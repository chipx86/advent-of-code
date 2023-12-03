#!/usr/bin/env python3
#
# Larry took us to a gondola lift, which takes us to the water source. He's
# also abandoning us. Probably off to play with his cubes.
#
# The gondolas aren't moving, though. But there's some engineer Elf -- we'll
# name him Carl -- and we have to help him because he's bad at his job.
#
# Turns out an engine part is missing, and nobody knows which one (again, bad
# at their job). So we have to add up all part numbers in the engine schematic,
# and find out which is missing.
#
# The schematic (our puzzle input) is a visual representation of the engine,
# with numbers and symbols without a defined meaning. But we do know that the
# numbers are part numbers for the symbol they're adjacent to (diagonally
# included).
#
#
# Approach
# --------
#
# So we have two things we need to do:
#
# 1. Parse out numbers from the input.
# 2. Find any adjacent symbols.
#
# I want to avoid loading everything into memory (imagine if this had a
# trillion rows!), but fortunately, we don't have to. For any line with a
# number, just need the row above and below it.
#
# So we'll scan each row for a number. Upon finding it, we'll:
#
# 1. Maintain a buffer for the characters comprising a number.
#
# 2. For each digit, look in all directions for a non-"." symbol.
#
# 3. If a symbol is found, we'll convert that buffer to an integer and add to
#    the total, providing the answer.
#
# We'll optimize this a bit by:
#
# 1. Avoiding looking left for any digit but the first one. Super minor, but
#    why do work we know we don't need to do.
#
# 2. If we see a symbol, stop scanning and just read the rest of the number,
#    since we don't use the symbol as anything but a flag indicating if the
#    number is part of the result.
#
# 3. Making sure we never have more than three rows in memory at a time.


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


def get_search_space(*, pre_line, scan_line, post_line, pos, first_digit):
    # Note that because of the newline at the end of the lines, we don't have
    # to worry about boundary issues on the right-hand side.
    if pre_line:
        # North-East
        yield pre_line, pos + 1

        # North
        yield pre_line, pos

        if pos > 0:
            # North-West
            yield pre_line, pos - 1

    if first_digit and pos > 0:
        # West
        yield scan_line, pos - 1

    # East
    yield scan_line, pos + 1

    if post_line:
        # South-East
        yield post_line, pos + 1

        # South
        yield post_line, pos

        if pos > 0:
            # South-West
            yield post_line, pos - 1


def get_answer():
    answer = 0

    with open('input', 'r') as fp:
        for pre_line, scan_line, post_line in scan_lines(fp):
            # Work our way through the line, looking for numbers.
            num_buffer = ''
            found_symbol = False

            # Note that the lines we're working with have a newline at the
            # end. This is a good thing! While this won't be a symbol, it
            # will trigger the end of number processing and calculating the
            # result for the number buffer.
            for pos, c in enumerate(scan_line):
                if c.isdigit():
                    # This is a part number.
                    num_buffer += c

                    # We'll only want to look for symbols if we haven't
                    # already found one.
                    if not found_symbol:
                        search = get_search_space(
                            pre_line=pre_line,
                            scan_line=scan_line,
                            post_line=post_line,
                            pos=pos,
                            first_digit=(len(num_buffer) == 1))

                        for search_line, pos in search:
                            search_c = search_line[pos]

                            if (search_c not in ('.', '\r', '\n') and
                                not search_c.isdigit()):
                                # We found a symbol.
                                found_symbol = True
                                break
                elif num_buffer:
                    # We found anything but a part number. If we were
                    # processing a part number, then we can now choose whether
                    # to factor it into the answer or discard it, depending on
                    # whether we found a suitable symbol.
                    if found_symbol:
                        answer += int(num_buffer)
                        found_symbol = False

                    num_buffer = ''

    return answer


answer = get_answer()
print(f'Answer = {answer}')
