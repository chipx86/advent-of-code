#!/usr/bin/env python3
#
# For this solution, I'm aiming to reduce runtime and memory costs.
#
# This is somewhat close to task1.py, though with some differences. I'll go
# over the approach.
#
# I have to load the entire dataset into RAM, but I do this by loading as
# bytes, avoiding initial text processing. These come in as character codes.
# Rather than an int(...) call to convert it, I can just use *MATH*,
# subtracting the character code of b'0' to get a number. Funny how that works.
#
# Not a huge optimization, but I'll take what I can get.
#
# These resulting integers go into tree_map, since I need to ultimately
# compare integers and use them as indexes. This differs from my approach in
# task1.py, which never needs to worry about actual numeric values.
#
# For each node in the tree, I store a list of:
#
#     [height, left_dist, right_dist, top_dist, bottom_dist]
#
# I try to keep runtime costs to a minimum. When I load the file, I load each
# line at a time and perform scans to calculate values (stored within the
# resulting loaded tree_map, as above) as I go. One left-to-right scan to
# calculate distance scores for each tree, and one right-to-left scan for the
# same.
#
# I then do the same thing for the vertical scans. One top-to-bottom, one
# bottom-to-top.
#
# During scans, to calculate distance scores, I keep track of the last
# position (relative to the boundary where the scan begins) of each height
# level. For each tree, I find the closest distance of all trees that are at
# least the current tree's height, and use that relative to the current
# position to store the distance. The height/distance trees then get updated
# as appropriate.
#
# To save a final computation loop to find the best tree, my final calculations
# for the end result are done in the bottom-to-top loops.
#
# At the point when this is processing data, I have everything I need to come
# up with the best tree candidates for each column. These are returned (by
# setting a flag), and the outer loop managing each set of vertical scans
# considers those for a final best tree calculation, which is then displayed.


MIN_CODE = ord(b'0')

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
        yield x, row[x]


def iter_rows(x, reverse=False):
    for y in iter_dir(tree_map_height, reverse=reverse):
        yield y, tree_map[y][x]


def scan_tree_scores(length, iterator, result_i, calc_best=False):
    last_height_pos = [None] * 10
    best_tree_score = None
    best_tree_i = None

    for pos, (i, row_data) in enumerate(iterator):
        h = row_data[0]

        # Find the closest tree. We'll only consider ones at least as tall
        # as this tree.
        closest_h = None

        for candidate_h in range(h, 10):
            candidate_pos = last_height_pos[candidate_h]

            if (candidate_pos is not None and
                (closest_h is None or
                 candidate_pos > last_height_pos[closest_h])):
                # This is a good candidate for the closest tree.
                closest_h = candidate_h

        if closest_h is None:
            # We didn't find a closest tree. The current tree can see all
            # the way to the border. Its distance is the current position
            # (0-based) relative to the border.
            row_data[result_i] = pos
        else:
            # We found a closest tree, meaning this tree is blocked. We can
            # use the difference in position of the current tree and that tree
            # to figure out the distance for the score.
            row_data[result_i] = pos - last_height_pos[closest_h]

        # Update the last position of this current height.
        last_height_pos[h] = pos

        if calc_best:
            tree_score = row_data[1] * row_data[2] * row_data[3] * row_data[4]

            if best_tree_score is None or tree_score > best_tree_score:
                # We found the best tree for this range.
                best_tree_score = tree_score
                best_tree_i = i

    return best_tree_score, best_tree_i


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

        # We'll store rows as:
        #
        # [height_value, left_distance, right_distance, top_distance,
        #  bottom_distance]
        row = [
            [c - MIN_CODE, 0, 0, 0, 0]
            for c in line
        ]

        # Calculate tree distane scores left-to-right.
        scan_tree_scores(tree_map_width,
                         iter_cols(row),
                         result_i=1)

        # And then right-to-left.
        scan_tree_scores(tree_map_width,
                         iter_cols(row, reverse=True),
                         result_i=2)

        tree_map.append(row)


# Complete a second pass, this time checking vertically. We'll also grab
# counts in this same reverse column loop.
best_spot_score = 0
best_spot_y = None
best_spot_x = None

for x in range(tree_map_width):
    # Calculate tree distance scores top-to-bottom.
    scan_tree_scores(tree_map_height,
                     iter_rows(x),
                     result_i=3)

    # And now bottom-to-top, calculating final results as we go.
    x_best_score, x_best_y = scan_tree_scores(tree_map_height,
                                              iter_rows(x, reverse=True),
                                              result_i=4,
                                              calc_best=True)

    if x_best_score > best_spot_score:
        # We have a new best score. Track that.
        best_spot_score = x_best_score
        best_spot_y = x_best_y
        best_spot_x = x


print(f'Best tree = {best_spot_x}, {best_spot_y} with '
      f'score = {best_spot_score}')
