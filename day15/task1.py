#!/usr/bin/env python3
#
# In today's task, we have a whole area full of sensors and beacons. Sensors
# will scan for the nearest beacon in all directions, and stop scanning when
# it finds one. The scan range kinda looks like a diamond, equal on all sides.
#
# There's a particular row our task needs us to pay attention to. We need to
# find out how much of that row is covered by sensors. Anything else (beacons
# or dead air) should be excluded. The coverage area is our answer.
#
# The input dataset produces a pretty big map, ove 4 million by 4 million
# positions. Knowing that, I didn't want to just populate a giant grid and
# then look at that row.
#
# I realized I could do this in one pass through the input dataset. But first,
# there's a couple things I needed to know:
#
# 1. The extents of a sensor scan area. This is determined by the first beacon
#    it finds, which can be in any direction relative to the sensor (and,
#    notably, each sensor will only ever find one beacon, as per the task
#    instructions).
#
#    This, it turns out, is easy! All you have to do is get the relative
#    X and Y offsets between the sensor and beacon, convert each to a
#    positive number if needed, and then add them together. This is the
#    max scan distance from the sensor's central position, along cardinal
#    directions.
#
#    Let me show an example. Here's a sensor (S) and beacon (B), with the
#    scan coverage (#).
#
#              #
#             ##B     <-- beacon line
#            #####
#           ###S###   <-- sensor line
#            #####
#             ###
#              #
#
#
#    Say the sensor is at (100, 100), and the beacon is at (101, 98).
#    The relative offset is (101 - 100, 98 - 100), or (1, -2). That's the
#    distance between the sensor and the beacon.
#
#    You could also flip that around, go beacon to sensor, giving us
#    (100 - 101, 100 - 98) == (-1, 2). It doesn't matter, because we're going
#    to convert to positive numbers: (1, 2).
#
#    We then add those numbers together. 1 + 2 == 3. That is the distance
#    between the sensor position and the further North, East, South, and West
#    values. Check above. Grab some graph paper and try it for other numbers.
#    It's always true.
#
#    So that was easy. Now we know the scan areas. Next up:
#
# 2. The scan width for a given row within that scan area.
#
#    This is also easy! It's basically the same thing. Let's look up above
#    and look at 2 rows below the sensor, the "###" row.
#
#    First, we need to know the row relative to the sensor. In the example
#    I just mentioned, it's 2 rows down. Cool, How do we compute the sensor
#    width? Easy. Take the width of the extents for the sensor's own row
#    (which is 3 in both directions), subtract the row offset. That'll give
#    us the extent from the sensor's X position on the given row. Double that,
#    account for the sensor, and we have the full width.
#
#    Let's try it:
#
#    Sensor extent: 3
#    Row offset: 2
#    Row 2's extent: 3 - 2 == 1
#    Double that for both extents: 1 * 2 == 2
#    Add the sensor: 2 + 1 == 3
#
#    There's our "###" width.
#
#    Now, below, I'm not doing *exactly* that. I'm just calculating the X
#    positions on either side of that scan range. But it's the same idea.
#    Take the X of the extents on the sensor's row, subtract the row offset,
#    and there's our X positions.
#
# Knowing that, I can do all this in one pass. For each sensor:
#
# 1. Get the outer extents of the sensor:
# 2. Make sure they overlap the target row (skipping if not).
# 3. Compute the distance between the sensor's Y and the target row.
# 4. With that, compute the sensor coverage for that row. Store each position
#    in a set of known positions.
# 5. If there's also a beacon on the target row, store that as well.
# 6. The answer is our sensor coverage minus any beacons.

import re


BEACON_RE = re.compile(
    r'^Sensor at x=(?P<sensor_x>-?\d+), y=(?P<sensor_y>-?\d+): closest beacon '
    r'is at x=(?P<beacon_x>-?\d+), y=(?P<beacon_y>-?\d+)'
)


TARGET_ROW = 2_000_000

target_row_scan_pos = set()
target_row_beacon_pos = set()


with open('input', 'r') as fp:
    for line in fp.readlines():
        m = BEACON_RE.match(line)
        assert m

        sensor_x = int(m.group('sensor_x'))
        sensor_y = int(m.group('sensor_y'))
        beacon_x = int(m.group('beacon_x'))
        beacon_y = int(m.group('beacon_y'))

        scan_dist = abs(beacon_x - sensor_x) + abs(beacon_y - sensor_y)

        scan_x1 = sensor_x - scan_dist
        scan_y1 = sensor_y - scan_dist
        scan_x2 = sensor_x + scan_dist
        scan_y2 = sensor_y + scan_dist

        # Check if the scan covers the target row.
        if scan_y1 <= TARGET_ROW <= scan_y2:
            # This scan does cover it. Let's find out by how much. */
            scanner_dy = abs(TARGET_ROW - sensor_y)
            row_x1 = scan_x1 + scanner_dy
            row_x2 = scan_x2 - scanner_dy

            # Store each position in that range (inclusive) in the set of
            # known positions. (There may be overlap, hence the set.)
            target_row_scan_pos.update(range(row_x1, row_x2 + 1))

        if beacon_y == TARGET_ROW:
            # There's a beacon on this row. We'll need to exclude that from
            # the final results.
            target_row_beacon_pos.add(beacon_x)


print('Coverage area for row %s: %s'
      % (TARGET_ROW, len(target_row_scan_pos - target_row_beacon_pos)))
