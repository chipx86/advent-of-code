#!/usr/bin/env python3
#
# Today's task is all about sand falling into a pit, condemning you to
# suffocation as the sand slowly engulfs the entire cavern.
#
# Well no, only if you get this task very, very wrong.
#
# In actuality, it's about modeling how the sand will fall. Each tick, sand
# drops either straight down, down and to the left, or down and to the right,
# until it can't drop anymore and is "at rest".
#
# But it must have something to drop on, and that's where the input data
# comes in. The data describes paths on a grid, mapping out the cave. The
# cave is perceived from the side, like an ant farm.
#
# For the map, you can of course store a big ol' grid of what's where, but
# I've been going for more optimal, memory/performance-efficient solutions,
# and a big grid of empty space is not efficient.
#
# There's so little on the map, that I opted for a dictionary/hashtable of
# coordinates instead. This is quick and easy to check, and we don't store
# any more than we need to. This also has the benefit of not having to worry
# so much about bounds checks.
#
# For parsing the map input, I just go line-by-line, splitting up the path
# into coordinates, computing all the intermediary positions between the
# previous position in the path and the current, and set all those in the
# hashtable.
#
# For dropping, I run a loop. Each tick, we figure out the three delta X
# positions in preferred order:
#
#      0 (vertical drop)
#     -1 (drop toward the left)
#      1 (drop toward the right)
#
# We then test that position by looking for something in our cave map
# hashtable. If we don't find anything, we can set that as the next position
# for the next iteration of the loop. If we do find something, we try the next
# delta, and if we exhaust all those options, the sand is at rest.
#
# Notably, if we drop out of the cave (the value is below the map height), we
# bail on any more sand. That's the condition in the first task.
#
# Rested sand counts are then tracked, giving me the answer.
#
# I also have drawing code in here to visualize the result of the drops. This
# was useful for debugging (though I actually had the logic right -- still
# nice to see). Because the cave is large, I keep track of the bounds of the
# map with anything interesting to show (initially set during map loading, and
# then updated as sand moves), which lets me draw just the parts of the map
# that I would have any interest in seeing.

import sys


# The initial position where all sand starts from.
SAND_SOURCE_POS = (500, 0)


# Some character codes for drawing.
ROCK = b'#'
AIR = b'.'
SAND_SOURCE = b'+'
SAND = b'o'


# The representation of the cave map.
#
# We're using a hashtable as the representation.
#
# Since the cave is mostly air, this takes up a lot less space than a grid
# of cells. It's also very quick to check and mutate.
cave_map = {
    SAND_SOURCE_POS: SAND_SOURCE,
}


# The boundaries and drawing viewport of the cave map.
cave_height = 0
cave_width = 0
cave_min_x1 = SAND_SOURCE_POS[0]
cave_min_y1 = SAND_SOURCE_POS[1]
cave_max_x2 = cave_min_x1
cave_max_y2 = cave_min_y1


def load_map():
    """Load the data from the map.

    This will parse the paths line-by-line, splitting them up into segments
    separated by " -> " markers, and then parsing out the resulting
    coordinates.

    We track the previous position and the current position for each step,
    and fill in all the gaps between those. Two positions are only ever
    connected by a straight horizontal or vertical line.
    """
    global cave_width, cave_height
    global cave_min_x1, cave_min_y1, cave_max_x2, cave_max_y2

    with open('input', 'rb') as fp:
        for line in fp.readlines():
            prev_pos = None

            for pos_str in line.strip().split(b' -> '):
                x, y = pos_str.split(b',')
                x = int(x)
                y = int(y)

                if prev_pos is None:
                    # Place a rock in this position. We don't want to assume
                    # there will be another place in the path.
                    cave_map[(x, y)] = ROCK
                elif prev_pos[0] != x:
                    # We're filling in gaps horizontally.
                    #
                    # Loop through each spot in the range and place a rock.
                    cave_map.update({
                        (temp_x, y): ROCK
                        for temp_x in range(min(x, prev_pos[0]),
                                            max(x, prev_pos[0]) + 1)
                    })
                elif prev_pos[1] != y:
                    # We're filling in gaps vertically.
                    #
                    # Loop through each spot in the range and place a rock.
                    cave_map.update({
                        (x, temp_y): ROCK
                        for temp_y in range(min(y, prev_pos[1]),
                                            max(y, prev_pos[1]) + 1)
                    })

                prev_pos = (x, y)

                # Update the stored boundaries to compute the map size and
                # display viewport.
                cave_width = max(cave_width, x + 1)
                cave_height = max(cave_height, y + 1)

                cave_min_x1 = min(cave_min_x1, x)
                cave_min_y1 = min(cave_min_y1, y)
                cave_max_x2 = max(cave_max_x2, x)
                cave_max_y2 = max(cave_max_y2, y)


def simulate_sand():
    """Simulate dropping all the sand out of the source.

    This will loop until we get a piece that falls out of bounds.

    Returns:
        int:
        The resulting amount of sand at rest. This will be our final answer.
    """
    global cave_width, cave_min_x1, cave_min_y1, cave_max_x2, cave_max_y2

    sand_at_rest = 0

    while True:
        sand_pos = drop_sand()

        if sand_pos is None:
            # We hit the end. We won't count this one. We only want the ones
            # that were at rest, not the ones that fell to their doom for all
            # eternity.
            break

        # Expand the known width and the viewport for drawing, if needed.
        cave_width = max(cave_width, sand_pos[0] + 1)
        cave_min_x1 = min(cave_min_x1, sand_pos[0])
        cave_min_y1 = min(cave_min_y1, sand_pos[1])
        cave_max_x2 = max(cave_max_x2, sand_pos[0])
        cave_max_y2 = max(cave_max_y2, sand_pos[1])

        cave_map[sand_pos] = SAND
        sand_at_rest += 1

    return sand_at_rest


def drop_sand():
    """Drop sand from a source position.

    This will drop a single piece of sand from a source position until it's
    at rest.

    Returns:
        tuple:
        A tuple of (x, y) of the at-rest position, or ``None`` if the sand
        fell out of bounds.
    """
    x, y = SAND_SOURCE_POS
    at_rest = False

    while not at_rest:
        # In order, we'll check:
        #
        # 1. If we can drop straight down.
        # 2. If we can drop down one and to the left.
        # 3. If we can drop down one and to the right.
        #
        # If any of these succeed, we'll continue the loop and process again.
        #
        # We'll assume we're at rest by default, unless we find we can set a
        # new position.
        at_rest = True

        for dx in (0, -1, 1):
            new_pos = (x + dx, y + 1)

            if new_pos not in cave_map:
                # We found a spot at this resting position.
                x, y = new_pos
                at_rest = False
                break

        # Check if we've already fallen out of the cave.
        if y >= cave_height:
            # We fell out of bounds.
            return None

    return x, y


def draw_map():
    """Draw the map, focusing only on the most interesting areas.

    We'll expand out the boundaries by a space on each side, adding some
    padding, and then draw out the map of the cave.
    """
    # Give us some padding around the viewport to better see around the edges
    # of drawn objects.
    x1 = max(cave_min_x1 - 1, 0)
    y1 = max(cave_min_y1 - 1, 0)
    x2 = cave_max_x2 + 2
    y2 = cave_max_y2 + 2

    # Now draw the cave, given the viewport.
    for y in range(y1, y2):
        sys.stdout.buffer.write(b''.join(
            cave_map.get((x, y), AIR)
            for x in range(x1, x2)
        ))

        print()


load_map()
sand_at_rest = simulate_sand()
draw_map()

print('Sand at rest = %s' % sand_at_rest)
