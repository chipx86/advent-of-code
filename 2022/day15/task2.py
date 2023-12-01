#!/usr/bin/env python3
#
# This task is more complicated than task1.py. You will need to read the
# description in task1.py before you continue.
#
# I'll wait.
#
# ...
#
# Done yet?
#
# Okay, so here's what's up. I'm not thrilled about my solution, because
# I feel it could be faster, but it's also not horribly slow. About 14 seconds
# on my machine.
#
# Let me explain.
#
# In this one, we have a boundary of 4 million by 4 million spots that that
# could have sensor coverage. And, in fact, *ALL* of those are covered, except
# for ONE single spot. That's 15,999,999,999,999 spots covered, and 1 spot
# not covered (which has a hidden beacon).
#
# We have to find that spot. To do that, we have to go row-by-row and find
# out if the entire row is in fact covered.
#
# This is expensive. That's 4 million rows! In each row, we need to figure
# out the coverage on that row (I describe this in task1.py), bearing in mind
# that multiple sensors may overlap, and find which row has that hidden beacon.
#
# I've put together some optimizations, in order to keep this from being any
# more expensive than necessary:
#
# 1. I try to eliminate sensors right off the bat. To do this, I sort through
#    the sensors and try to find any that overlap the same area. If I find
#    any (I found one!), I discard them.
#
#    I suspect there would be some benefit to a more complex algorithm here
#    that optimizes out sensors that are obscured by the union of multiple
#    sensor scans, but I opted not to go too far into this.
#
# 2. I keep sensors in Y order, and I take advantage of that to create a
#    sliding window of eligible sensors while scanning down the rows. This
#    lets me discard sensors that no longer apply (due to being above the
#    current row), and skip any sensors that won't yet apply (due to being
#    below).
#
# I go into more detail on these below.
#
# Things I attempted or considered but threw out:
#
# 1. I tried to optimize the initial list of sensors, immediately throwing out
#    any that had scans outside the target grid, but there weren't any. So
#    I deleted that logic.
#
# 2. I tried shortened the search space by determining if there were any rows
#    or columns not covered by sensors to begin with, but there weren't, and
#    that wouldn't make a ton of sense, given we're trying to locate a single
#    uncovered spot.
#
# 3. I tried alternate approaches to storing the ranges, with an eye toward
#    eliminating a sort. Nothing was really efficient enough. The problem
#    stemmed from not being able to order sensors by X for a given row ahead
#    of time. So it was still more efficient to build the list of ranges and
#    *then* sort through them.
#
# 4. I also tried to filter in my inner sensor scan loop when processing a row,
#    throwing out or capping ranges. While not normally expensive, it was just
#    expensive enough to add to the runtime costs.

import re


BEACON_RE = re.compile(
    r'^Sensor at x=(?P<sensor_x>-?\d+), y=(?P<sensor_y>-?\d+): closest beacon '
    r'is at x=(?P<beacon_x>-?\d+), y=(?P<beacon_y>-?\d+)'
)


BEACON_MIN = 0
BEACON_MAX = 4_000_000

TUNING_FREQ_MULTIPLIER = 4_000_000


# Load all the sensor data.
raw_sensors = []

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

        # We could only consider sensors that have scans somewhere within the
        # min/max beacon range, but in our input data, they all are. So
        # that's not an optimization win.
        raw_sensors.append((sensor_y, scan_x1, scan_y1, scan_x2, scan_y2))


# There are sensors in the input data that overlap in coverage area. Well,
# there's one, at least (maybe more?), but given how many rows we have to
# check, removing just one sensor can do quite a lot! Let's get rid of it.
#
# We'll do this by sorting by (Y1, X1), and checking overlap between
# consecutive sensors. Any that fully overlap the previous scanner's area
# can easily go.
#
# This sort order will also help us when we scan each row. I'll go into that
# below.
prev_s = None
sensors = []

for s in sorted(raw_sensors,
                key=lambda s: (s[2], s[1])):
    if (prev_s is None or
        not (s[1] >= prev_s[1] and s[2] >= prev_s[2] and
             s[3] <= prev_s[2] and s[4] <= prev_s[4])):
        sensors.append(s)
        prev_s = s

print('Eliminated %s overlapping sensor(s)'
      % (len(raw_sensors) - len(sensors)))


# We'll be scanning from top to bottom. Conveniently, our sensors are now
# also ordered from top to bottom!
#
# This is another optimization trick. Since they're ordered, we'll be able to
# select the window of sensors applicable to the current location. Anything
# outside of the scan range will be ignored.
#
# But not just ignored. Eliminated from checks. If a sensor scan's Y2 ends
# before the current row, we can outright delete it from further checks,
# because we'll never use it again.
#
# Similarly, if a sensor scan's Y1 comes after the scan row, we know that
# all subsequent sensors will as well (given the sort), so we can just end
# that sensor loop.
#
# Otherwise, the plan of attack is:
#
# 1. Loop through each row.
# 2. For each row, loop through each sensor.
# 3. For each applicable sensor, compute the coverage range and add it to
#    row_scan_data.
# 4. Sort row_scan_data and check if there are any gaps between ranges. If
#    there are, we found our hidden beacon, and we can stop!
#
#    (I want to get rid of this sort, but I think I need it. At least with
#    this current approach.)
discard_sensors = []
found_pos = None

for y in range(BEACON_MIN, BEACON_MAX + 1):
    row_scan_data = []

    for sensor in sensors:
        sensor_y, scan_x1, scan_y1, scan_x2, scan_y2 = sensor

        if scan_y1 > y:
            # There are no more candidate sensors to check for this row.
            # All the following sensors are too low to bother checking. We're
            # done with this row, and can start analyzing data.
            break
        elif scan_y2 < y:
            # This sensor doesn't cover this far down. We'll never need to
            # process this sensor again. We can discard it.
            discard_sensors.append(sensor)
        else:
            # Figure out the distance between this Y position and our sensor.
            # That will be the amount we need to shave off the width of our
            # total scanner range, to get the coverage for this row.
            scanner_dy = abs(y - sensor_y)
            row_x1 = scan_x1 + scanner_dy
            row_x2 = scan_x2 - scanner_dy

            # The scanned area is within the confirmed beacon range. Add
            # it to a list of covered rows for further processing.
            row_scan_data.append((row_x1, row_x2 + 1))

    # We'll now check if we have a contiguous list of ranges. If there's any
    # gap in our coverage, we know we've found the beacon.
    x = BEACON_MIN

    for scan_x1, scan_x2 in sorted(row_scan_data):
        # There are other ways I could have organized this logic, but I'm
        # going for readability here (explaining each step).
        if scan_x2 <= x:
            # There's an overlap. Skip it.
            continue
        elif scan_x1 > x:
            # We found it! Set the flag, and we'll then bail further down.
            found_pos = (scan_x1 - 1, y)
            break

        # Update the end of the range for the next check.
        x = scan_x2

    if found_pos:
        # We found the beacon! Good job, us!
        break

    # If we have any sensors to discard, do so now.
    if discard_sensors:
        for sensor in discard_sensors:
            sensors.remove(sensor)

        discard_sensors = []


print('Found the beacon at %s, %s' % found_pos)
print('Frequency = %d'
      % (TUNING_FREQ_MULTIPLIER * found_pos[0] + found_pos[1]))
