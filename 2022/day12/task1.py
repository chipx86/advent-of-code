#!/usr/bin/env python3
#
# Today's task is to find the shortest path (number of steps) from a starting
# location to a destination location, using a heightmap of characters a..z that
# depict elevation.
#
# For shortest path, I go with Djikstra's algorithm, which is fast. There's a
# good overview of it here: https://www.programiz.com/dsa/dijkstra-algorithm
#
# As usual for my solutions on these tasks, I'm trying to avoid long processing
# times or memory usage. Djikstra's algorithm helps with the processing time.
#
# For memory, I'm choosing to keep my representation of the height map (input
# file) as simple as possible. Instead of some fancy data structure or even
# nested arrays pointing to integers, I'm reading in as lists of byte strings.
# Each row is a byte string in an array. These are fast to scan, cheap to
# store, and still give me integers (representing character codes) when
# indexing into the string.
#
# We don't actually care what the values are for each position in the map, just
# that they're consistently relative to each other, so that means there's no
# reason to normalize any of the values. The character code for 'a' is one
# lower than for 'b', but it doesn't matter what those character codes are.

from heapq import heappush, heappop


def iter_neighbors(*, x, y, max_height):
    """Iterate through all reachable neighbors.

    This takes a starting position, and a maximum allowable height.

    Args:
        x (int):
            The X position all neighbors are relative to.

        y (int):
            The Y position all neighbors are relative to.

        max_height (int):
            The maximum height allowed for a neighbor.

    Yields:
        tuple:
        Each neighbor position in (x, y) form.
    """
    candidates = [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
    ]

    # Go through those. If they're within bounds, and either one level
    # higher or any level lower, we can process it.
    for candidate_x, candidate_y in candidates:
        if (0 <= candidate_x < heightmap_width and
            0 <= candidate_y < heightmap_height and
            heightmap[candidate_y][candidate_x] <= max_height):
            yield candidate_x, candidate_y


def get_shortest_path_steps(start_pos, end_pos):
    """Find the number of steps for the shortest path between two positions.

    This uses Djikstra's algorithm to quickly find the shortest path.

    Args:
        start_pos (tuple):
            A starting position of (x, y).

        end_pos (tuple):
            An ending position of (x, y).

    Returns:
        int:
        The number of steps in the shortest path.
    """
    to_visit = {start_pos}
    distances = {start_pos: 0}
    parents = {}

    while to_visit:
        # Find the nearest position to start with.
        current_pos = min(to_visit, key=lambda node: distances[node])

        # Remove that from the visit list, so we don't try it again.
        to_visit.remove(current_pos)

        if current_pos == end_pos:
            # We're done!
            break

        # Start figuring out which adjacent spaces we should check next.
        current_x, current_y = current_pos
        max_candidate_height = heightmap[current_y][current_x] + 1

        for neighbor_pos in iter_neighbors(x=current_x,
                                           y=current_y,
                                           max_height=max_candidate_height):
            # It matches the criteria. This is a traversable candidate
            # neighbor of sufficient height.
            distance = distances[current_pos] + 1

            if (neighbor_pos not in distances or
                distance < distances[neighbor_pos]):
                # We haven't processed this position yet, or it's closer
                # than it was from another path, so begin tracking it
                # and queue it up for possible visits.
                distances[neighbor_pos] = distance
                parents[neighbor_pos] = current_pos
                to_visit.add(neighbor_pos)

    # We found a path. We're now going to walk the paths to get the step count.
    last_pos = end_pos
    i = 0

    while last_pos != start_pos:
        i += 1
        last_pos = parents[last_pos]

    return i


heightmap = []
heightmap_width = None
heightmap_height = None
heightmap_start_pos = None
heightmap_end_pos = None


with open('input', 'rb') as fp:
    # We could use any representation for the map, but we'll go with lists
    # of byte strings. This is just to save on memory. When accessing by
    # index, we'll get an integer of the character code, which can be used for
    # height comparison.
    heightmap = []

    for y, line in enumerate(fp.readlines()):
        line = line.rstrip()

        # Look for the start position.
        if heightmap_start_pos is None:
            x = line.find(b'S')

            if x != -1:
                heightmap_start_pos = (x, y)

                # Swap out the 'S' for an 'a', to keep height maps consistent.
                line = b'%sa%s' % (line[:x], line[x + 1:])

        # Look for the end position.
        if heightmap_end_pos is None:
            x = line.find(b'E')

            if x != -1:
                heightmap_end_pos = (x, y)

                # Swap out the 'E' for a 'z', to keep height maps consistent.
                line = b'%sz%s' % (line[:x], line[x + 1:])

        heightmap.append(line)

    # We've built our height map. Store the width and heights of the map,
    # assert we found our starting values, and then move on.
    heightmap_width = len(heightmap[0])
    heightmap_height = len(heightmap)

    assert heightmap_start_pos
    assert heightmap_end_pos

    # Find the shortest path to the target.
    steps = get_shortest_path_steps(heightmap_start_pos, heightmap_end_pos)

    print(f'Minimum steps to target = {steps}')
