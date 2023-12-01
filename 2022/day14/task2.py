#!/usr/bin/env python3
#
# In task2.py, we have the same "oh no all the sand!" issue we had in task1.py,
# but this time it turns out we're standing on a floor and not just levitating
# in panic.
#
# That's good news, right?
#
# So, we don't have to worry about sand falling into the deep dark void, and
# we can rest assured that the sand will eventually plug up the hole emitting
# the sand, given the rules of how sand is falling.
#
# That's totally how it works.
#
# Anyway, we're dropping the out-of-bounds check in favor of a floor Y position
# check. And, well, I guess that's about it for the changes, basically.

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


# The location of the infinitely-long floor.
cave_floor_y = None


def load_map():
    """Load the data from the map.

    This will parse the paths line-by-line, splitting them up into segments
    separated by " -> " markers, and then parsing out the resulting
    coordinates.

    We track the previous position and the current position for each step,
    and fill in all the gaps between those. Two positions are only ever
    connected by a straight horizontal or vertical line.
    """
    global cave_width, cave_height, cave_floor_y
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
                #
                # We won't bother setting cave_max_y2 here, because we know
                # we'll need to calculate this at the end given the floor
                # location.
                cave_width = max(cave_width, x + 1)
                cave_height = max(cave_height, y + 1)

                cave_min_x1 = min(cave_min_x1, x)
                cave_min_y1 = min(cave_min_y1, y)
                cave_max_x2 = max(cave_max_x2, x)

        # Calculate the floor position and expand the viewport to match.
        cave_floor_y = cave_height + 1
        cave_height = cave_floor_y + 1
        cave_max_y2 = cave_height


def simulate_sand():
    """Simulate dropping all the sand out of the source.

    This will loop until the source of the sand gets plugged up.

    Returns:
        int:
        The resulting amount of sand at rest. This will be our final answer.
    """
    global cave_width, cave_min_x1, cave_min_y1, cave_max_x2, cave_max_y2

    sand_at_rest = 0

    while True:
        sand_pos = drop_sand()
        sand_at_rest += 1

        # Expand the viewport for drawing, if needed.
        #
        # We know we'll never need to expand cave_max_y2, since nothing will
        # fall past the floor.
        cave_width = max(cave_width, sand_pos[0] + 1)
        cave_min_x1 = min(cave_min_x1, sand_pos[0])
        cave_min_y1 = min(cave_min_y1, sand_pos[1])
        cave_max_x2 = max(cave_max_x2, sand_pos[0])

        # Unlike in task1.py, we won't be dealing with a None value. Instead,
        # we need to bail here once we know we've overlapped the source,
        # blocking the sand and ending the sand-dropping process.
        if sand_pos == SAND_SOURCE_POS:
            cave_map[SAND_SOURCE_POS] = SAND
            break

        cave_map[sand_pos] = SAND

    return sand_at_rest


def drop_sand():
    """Drop sand from a source position.

    This will drop a single piece of sand from a source position until it's
    at rest.

    Unlike in task1.py, we don't have to worry about out-of-bounds locations
    (so no more ``None`` result), but we do have to consider the floor's Y
    location.

    Returns:
        tuple:
        A tuple of (x, y) of the at-rest position.
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
        # Note that in task2.py, we not only need to check the map, but the
        # floor location as well.
        at_rest = True

        if y + 1 == cave_floor_y:
            # We hit the floor. We're done.
            break

        for dx in (0, -1, 1):
            new_pos = (x + dx, y + 1)

            if new_pos not in cave_map:
                # We found a spot at this resting position.
                x, y = new_pos
                at_rest = False
                break

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
