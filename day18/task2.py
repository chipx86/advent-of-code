#!/usr/bin/env python3
#
# In part 2, we have to find out how many external visible surfaces there are.
# If a surface is inside of the structure, unreachable by any "water" or
# "steam" on the outside, then we don't want to count it.
#
# I took the same approach from task 1, and stepped it up a bit.
#
# Basically, if we knew the up-front visible surface count, and we then occlude
# all externally-accessible surfaces, we'll know how many internal "visible"
# surfaces there are. The difference between those numbers is our answer.
#
# To do that, I flood-fill the exterior. I first ensure there's a one-cube-wide
# gap around the entire exterior of the cube structure, and then I flood fill
# from a starting position.
#
# The flood fill is designed to be.. somewhat quick. I wish it were faster.
#
# What I'm doing there is having a single function managing a flood queue. It
# takes a starting position, adds it to the queue, and processes. During
# processing, floods occur along X, then Y, then Z axis, starting at that
# position, and going in either direction until a cube would be hit.
#
# Along the way, each surface encountered is occluded.
#
# Caches of visited cube positions and newly-occluded cube positions are used
# to ensure we don't repeat actions and take too long.
#
# All-in-all, it's quick enough. About 300ms locally. Some improvements could
# be made, for sure, but I'll take it for this task.

import sys
from collections import deque


# Tracking of all placed cube positions.
#
# Each entry is a (X, Y, Z) position of a cube, using standard cube coordinates
# from the input dataset.
cubes = set()


# Tracking of all visible surface positions.
#
# Each entry is a (X, Y, Z) position of a surface (using increments of 0.5
# for coordinates -- see get_cube_surface_positions().
visible_surfaces = set()


# Tracking of all occluded surface positions.
#
# Each entry is a (X, Y, Z) position, same as in visible_surfaces.
occluded_surfaces = set()


# Minimum/maximum position extents for cube placement.
min_x = sys.maxsize
min_y = sys.maxsize
min_z = sys.maxsize
max_x = 0
max_y = 0
max_z = 0


def get_cube_surface_positions(x, y, z):
    """Return a series of surface positions for a given cube position.

    I decided to go with a coordinate system that let me easily map
    X, Y, and Z to surface positions.

    For this, each coordinate number can have the following relative
    values:

    Each position will be a decimal number. A relative -1 represents the
    left/top/back surface of a cube, a 0.5 represents the middle (in other
    words, no surface along that axis to worry about), and the position (+0)
    represents the right/bottom/back surface of a cube.

          -1: The surface is to the left/top/back of the cube.

        -0.5: The middle of the cube. There's no actual surface data
              encoded here. Important for tracking just a left-most,
              top-most, etc. surface while retaining the cube's
              coordinates as part of the storage.

          +0: The surface is to teh right/bottom/front of the cube.

    Args:
        x (int):
            The X coordinate of the cube.

        y (int):
            The Y coordinate of the cube.

        z (int):
            The Z coordinate of the cube.

    Returns:
        tuple of int:
        A 3-tuple of (surface_x, surface_y, surface_z), as outlined above.
    """
    return (
        (x - 1,   y - 0.5, z - 0.5),
        (x,       y - 0.5, z - 0.5),
        (x - 0.5, y - 1,   z - 0.5),
        (x - 0.5, y,       z - 0.5),
        (x - 0.5, y - 0.5, z - 1  ),
        (x - 0.5, y - 0.5, z      ),
    )


def expand_steam_dir(start_pos, i_range, start_i, delta,
                     to_visit, occluded_cubes):
    """Expand steam in a given direction.

    This will flood fill in two directions from a starting location, as
    indicated by the range an delta.

    The flood fill will go until a cube is hit. Along the way, any surfaces it
    comes into contact with will be marked as occluded.

    Args:
        start_pos (tuple of int):
            A 3-tuple of the starting position to fill from.

        i_range (tuple of int):
            A 2-tuple of the starting and ending range for the fill along the
            desired axis, inclusive.

        start_i (int):
            The starting coordinate within the axis to flood fill from.

        delta (tuple of int):
            A 3-tuple of deltas used to determine the path to fill. This will
            be a tuple of (X, Y, Z), with only one value being 1, the others 0.

        to_visit (set):
            A set of coordinates that need to be visited. Anything along this
            path that hasn't been occluded will be marked as visited.

        occluded_cubes (set):
            A set of occluded cube positions that can be skipped. Any position
            we occlude will be added to this set.
    """
    min_i, max_i = i_range
    x, y, z = start_pos
    dx, dy, dz = delta

    # We're going to expand the steam in two directions:
    #
    # 1. Left/back/up from the starting position.
    # 2. Right/front/down from one position after the starting position.
    #
    # We'll do this until we either hit the end position (in which case we're
    # done) or we hit a cube (in which case we'll stop traversing that
    # direction).
    #
    # Any valid spot will result in surfaces being removed.
    for traverse_range in ((0, -start_i - min_i - 1, -1),
                           (1, start_i + max_i + 1)):
        for i in range(*traverse_range):
            # This will give us a position along the path. The delta values
            # (1, 0, 0), (0, 1, 0), or (0, 0, 1) are used to generate relative
            # indexes on top of the starting position.
            pos = (
                x + dx * i,
                y + dy * i,
                z + dz * i,
            )

            if pos in cubes:
                # We found a cube. Stop traversing in this direction.
                break

            if pos not in occluded_cubes:
                # This position isn't obscured. Let's change that.
                for surface_pos in get_cube_surface_positions(*pos):
                    try:
                        visible_surfaces.remove(surface_pos)
                        occluded_surfaces.add(surface_pos)
                    except KeyError:
                        pass

                occluded_cubes.add(pos)

                # Re-visit this, in case we need to check another direction.
                to_visit.add(pos)


def expand_steam(start_pos):
    """Expand steam in all cardinal directions, starting from a given position.

    This will expand the steam from a position, going up, down, left, right,
    and side-to-side. Each position expanded into will then expand again into
    new directions.

    Any position expanded into that does not have a cube in it will have all
    surfaces occluded, reducing the total visible surface count. This is used
    to help us get an answer at the end.

    This is implemented with a :py:class:`set` as the queue, making it easy to
    avoid re-processing entries that have been visited before. This also means
    we don't have to recurse every time we want to fill from a new starting
    position.

    Args:
        start_pos (tuple of int):
            A 3-tuple of the starting position to fill from.
    """
    occluded_cubes = set()
    visited = set()
    queue = {start_pos}

    while queue:
        pos = queue.pop()
        x, y, z = pos

        if (pos not in visited and
            min_x <= x <= max_x and
            min_y <= y <= max_y and
            min_z <= z <= max_z):
            visited.add(pos)

            for delta, i_range, start_i in (((1, 0, 0), (min_x, max_x), x),
                                            ((0, 1, 0), (min_y, max_y), y),
                                            ((0, 0, 1), (min_z, max_z), z)):
                expand_steam_dir(start_pos=pos,
                                 i_range=i_range,
                                 start_i=start_i,
                                 delta=delta,
                                 to_visit=queue,
                                 occluded_cubes=occluded_cubes)


def main():
    """Main logic for the program.

    This will read through the input and place cubes (technically, track
    visible/occluded surface positions for cubes).

    It will track how many visible surfaces there are, and then "expand steam"
    to occlude all remaining visible surfaces reached from the outside. That
    will leave only the surfaces inside the object that steam could not expand
    into.

    The delta between those two numbers is our answer.
    """
    global min_x, max_x
    global min_y, max_y
    global min_z, max_z

    with open('input', 'r') as fp:
        for line in fp.readlines():
            x, y, z = [
                int(_i)
                for _i in line.strip().split(',')
            ]

            # Note that we're adding a 1 cube gap around the entire perimeter.
            # This will help us flood-fill everything to find any surfaces that
            # need to be obscured later.
            min_x = min(min_x, x - 1)
            min_y = min(min_y, y - 1)
            min_z = min(min_z, z - 1)
            max_x = max(max_x, x + 1)
            max_y = max(max_y, y + 1)
            max_z = max(max_z, z + 1)

            cubes.add((x, y, z))

            for pos in get_cube_surface_positions(x, y, z):
                if pos not in occluded_surfaces:
                    if pos in visible_surfaces:
                        visible_surfaces.remove(pos)
                        occluded_surfaces.add(pos)
                    else:
                        visible_surfaces.add(pos)

    # This is our total number of visible surfaces, interior and exterior.
    num_surfaces = len(visible_surfaces)

    # Now "expand the steam", which will flood fill around the whole perimeter
    # of our cubes, deleting any stored surfaces we find. What's left will be
    # the surfaces that couldn't be reached. Our initial surface count minus
    # what's remaining is our answer. That will be the total number of surfaces
    # reachable.
    expand_steam((min_x, min_y, min_z))
    num_surfaces -= len(visible_surfaces)

    print('Number of surfaces = %s' % num_surfaces)


if __name__ == '__main__':
    main()
