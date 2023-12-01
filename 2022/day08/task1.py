#!/usr/bin/env python3
#
# For this solution, I'm aiming to reduce runtime and memory costs.
#
# I have to load the entire dataset into RAM, but I do this by loading as
# bytes, avoiding any text processing. I can then process the tree as a series
# of character codes. I don't actually need numbers in this task, so I just
# compare based on what's effectively a "-1", by way of EDGE_CODE. This lets
# me easily compare values, without needing to parse integers or store Unicode
# strings.
#
# Mainly, I'm optimizing for runtime performance.
#
# For that, I try to keep scans to a minimum. When I load the file, I load
# each line at a time and perform scans to calculate values (stored within
# the resulting loaded tree_map) as I go. One left-to-right scan to calculate
# visibility, and one right-to-left scan for the same.
#
# I then do the same thing for the vertical scans. One top-to-bottom, one
# bottom-to-top.
#
# To save a final computation loop, my final calculations for the end result
# are done in that bottom-to-top loop. At the point when this is processing
# data, I have everything I need to come up with a visibility total, so I just
# set a flag to compute values, return that from the function, and add that
# to a grand total for display.


EDGE_CODE = ord(b'0') - 1

tree_map_width = None
tree_map_height = 0
tree_map = []


def iter_dir(length, reverse=False):
    if reverse:
        for i in range(length):
            yield length - i - 1
    else:
        for i in range(length):
            yield i


def iter_cols(row, reverse=False):
    for x in iter_dir(tree_map_width, reverse=reverse):
        yield row[x]


def iter_rows(x, reverse=False):
    for y in iter_dir(tree_map_height, reverse=reverse):
        yield tree_map[y][x]


def scan_visibility(iterator, calc_count=False):
    max_code = EDGE_CODE
    visible_count = 0

    for row_data in iterator:
        c = row_data[0]

        if max_code < c:
            row_data[1] = True
            max_code = c

        if calc_count and row_data[1]:
            visible_count += 1

    return visible_count


with open('input', 'rb') as fp:
    # Read through each line, processing the visibility map horizontally
    # as we go.
    for line in fp.readlines():
        line = line.strip()
        tree_map_height += 1

        if tree_map_width is None:
            tree_map_width = len(line)
        else:
            # Just make sure we don't have anything funky in our data.
            assert tree_map_width == len(line)

        # We'll store rows as [char_code, is_visible]
        row = [
            [c, False]
            for c in line
        ]

        # Calculate visible trees left-to-right.
        scan_visibility(iter_cols(row))

        # And then right-to-left.
        scan_visibility(iter_cols(row, reverse=True))

        tree_map.append(row)


# Complete a second pass, this time checking vertically. We'll also grab
# counts in the bottom-to-top loop, avoiding having to loop through again.
visible_count = 0

for x in range(tree_map_width):
    # Calculate visibility top-to-bottom.
    scan_visibility(iter_rows(x))

    # And now bottom-to-top, calculating final results as we go.
    visible_count += scan_visibility(iter_rows(x, reverse=True),
                                     calc_count=True)


print(f'Visible trees = {visible_count}')
