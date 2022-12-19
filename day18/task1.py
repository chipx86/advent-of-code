#!/usr/bin/env python3
#
# In today's task, we're dealing with lava falling into water and creating
# obsidian cubes. We're basically Minecraft right now.
#
# The trick is, we need to know how many visible surfaces remain at the end.
# One cube by itself has 6 surfaces, but if two cubes are right up against each
# other, a shared surface becomes occluded, and so we only have 10 visible
# surfaces, rather than 12.
#
# There are many ways to approach this problem. I went with minimizing the
# amount of data I have to store and the amount of post-processing needed.
#
# In my approach, we track sets of visible and occluded surfaces. We iterate
# through the positions, calculate the surface positions, and then figure out
# what to do with it.
#
# If the surface has no state in it, we set it. However, if there's already a
# surface tracked, we know we're going to occlude it, so we remove it and store
# it in occluded_surfaces instead.
#
# This is really nice for a couple reasons:
#
# 1. It's a lot less to store. We don't need to figure out the dimensions
#    up-front (or resize as we go), and we don't have wasted space (many
#    positions are *not* taken up by cubes).
#
# 2. Since we're maintaining a list of visible surfaces, our answer is just the
#    length of that set of results.
#
# Super cheap, super fast.
#
# But will it scale? Stay tuned for part 2.


# Tracking of all visible surface positions.
#
# Each entry is a (X, Y, Z) position of a surface (using increments of 0.5
# for coordinates -- see get_cube_surface_positions().
visible_surfaces = set()


# Tracking of all occluded surface positions.
#
# Each entry is a (X, Y, Z) position, same as in visible_surfaces.
occluded_surfaces = set()


with open('input', 'r') as fp:
    for line in fp.readlines():
        x, y, z = [
            int(_i)
            for _i in line.strip().split(',')
        ]

        # Calculate surface positions.
        #
        # I decided to go with a coordinate system that let me easily map
        # X, Y, and Z to surface positions.
        #
        # For this, each coordinate number can have the following relative
        # values:
        #
        #       -1: The surface is to the left/top/back of the cube.
        #
        #     -0.5: The middle of the cube. There's no actual surface data
        #           encoded here. Important for tracking just a left-most,
        #           top-most, etc. surface while retaining the cube's
        #           coordinates as part of the storage.
        #
        #       +0: The surface is to teh right/bottom/front of the cube.
        for pos in ((x - 1,   y - 0.5, z - 0.5),
                    (x,       y - 0.5, z - 0.5),
                    (x - 0.5, y - 1,   z - 0.5),
                    (x - 0.5, y,       z - 0.5),
                    (x - 0.5, y - 0.5, z - 1  ),
                    (x - 0.5, y - 0.5, z      )):
            if pos not in occluded_surfaces:
                if pos in visible_surfaces:
                    visible_surfaces.remove(pos)
                    occluded_surfaces.add(pos)
                else:
                    visible_surfaces.add(pos)

    print('Number of surfaces = %s' % len(visible_surfaces))
