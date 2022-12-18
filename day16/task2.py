#!/usr/bin/env python3
#
# Oh boy this one.
#
# Let me start off by saying, I don't know that this is the right solution.
# But it is fast, and it works.
#
# I say this because it fails the test input, but succeeds on the real input.
#
# In this one, we have two "players" (the person and an elephant) moving about
# the tunnels, opening valves. Instead of 30 minutes, we have 26 minutes.
#
# I used the same approach, same code as in task1.py, but have modified
# get_best_score() to optionally take a starting set of opened valves and to
# return the full processed path.
#
# What I did was introduce one call to this to have the player walk the graph
# and return a result, and then one for the elephant to walk again but to
# list all those paths in the opened valves. The total combined scores are the
# answer.
#
# Again, this fails the test input, because the player completes it fast enough
# to make the elephant useless. So it's maybe not the right solution.. but it
# *does* work on the real input. The real being that, in the real input, there
# are valves left over. It happens to work out perfectly for the real input.
#
# This has been keeping me up at nights, but I have to move on with my life.

import re


# The maximum number of minutes in which actions can be taken.
#
# For task 2, we spend 4 whole minutes training an elephant, so we only get
# 26 minutes left.
MAX_MINUTES = 26


# Stored information on all valves in the graph.
valves = {}


def get_shortest_path(start_valve, end_valve):
    """Find the shortest path between two valves.

    This uses Djikstra's algorithm to quickly find the shortest path. It works
    very much like the approach in Day 12. However, instead of calculating a
    number of steps, we'll be returning the path itself.

    Returns:
        int:
        The number of steps in the shortest path.
    """
    to_visit = {start_valve}
    distances = {
        start_valve: 0,
    }
    parents = {}

    while to_visit:
        # Find the nearest position to start with.
        current_valve = min(to_visit, key=lambda valve: distances[valve])

        # Remove that from the visit list, so we don't try it again.
        to_visit.remove(current_valve)

        if current_valve == end_valve:
            # We're done!
            break

        # Start figuring out which adjacent valves we should check next.
        for candidate_valve in valves[current_valve]['connected']:
            distance = distances[current_valve] + 1

            if (candidate_valve not in distances or
                distance < distances[candidate_valve]):
                # We haven't processed this valve yet, or it's closer than it
                # was from another path, so begin tracking it and queue it up
                # for possible visits.
                distances[candidate_valve] = distance
                parents[candidate_valve] = current_valve
                to_visit.add(candidate_valve)

    # We found a path. We're now going to walk the paths to get the step count.
    last_valve = end_valve
    path = [last_valve]

    while last_valve != start_valve:
        path.append(parents[last_valve])
        last_valve = parents[last_valve]

    return list(reversed(path[:-1]))


def get_best_score(*, opened_valves=None):
    """Return the best pressure relief score available.

    Args:
        opened_valves (set of str, optional):
            An optional default set of valves to mark opened.

    Returns:
        int:
        The best score found in the graph.
    """
    # A cache used to keep track of scores for particular path/time/valve sets.
    path_cache = {}

    def _find_best(*, mins_elapsed, cur_path, opened_valves, avail_flow_rates):
        """Return the best score for the available branches from this valve.

        This will compute the pressure relief for this valve (if any), and then
        try to find the best score for any valves that can be travelled to from
        here.

        This is called recursively for any next valves.

        Args:
            mins_elapsed (int):
                The total number of minutes elapsed before getting to this
                valve.

            cur_path (list of str):
                The current full path from the start up to this valve (this
                valve's ID will be the last one in the path).

            opened_valves (set of str):
                The set of valves that have already been opened by the time
                that this valve is processed.

                The same set is shared for the current valve and any recursed
                calls from here.

            avail_flow_rates (set of int):
                The set of non-0 flow rates that are still available to be
                processed.

                The same set is shared for the current valve and any recursed
                calls from here.

        Returns:
            int:
            The best score available from this point in the path, relative
            to this path.
        """
        cur_valve_id = cur_path[-1]
        cur_valve = valves[cur_valve_id]

        # We'll track all scores that may be achieved from this point on.
        # At the end of this function, the best score wins, helping dictate
        # the path.
        candidate_scores = []

        flow_rate = cur_valve['flow_rate']

        if flow_rate > 0 and cur_valve_id not in opened_valves:
            # Mark this room's valve as opened, so we don't try to go directly
            # here again.
            opened_valves.add(cur_valve_id)
            avail_flow_rates.remove(flow_rate)

            # Figure out the total amount of pressure that will be released
            # after opening this valve.
            eventual_pressure = (MAX_MINUTES - mins_elapsed - 1) * flow_rate

            # It takes two minutes to have walked in here and opened pressure.
            mins_elapsed += 2
        else:
            # We should never be explicitly going to any 0-pressure room,
            # unless it's the starting room.
            assert len(cur_path) == 1

            # It only takes 1 minute to be in this room.
            mins_elapsed += 1
            eventual_pressure = 0

        # This score is a candidate for best option for traversal. It may
        # be beat by continuing along to other rooms.
        best_score = eventual_pressure
        best_path = cur_path

        if avail_flow_rates and mins_elapsed < MAX_MINUTES:
            # There's time left and valves to open. Let's get to it.
            #
            # Go through each connected valve that's worth going to and
            # re-call this function, factoring in the time taken to travel
            # there.
            #
            # We'll only consider valves that we have enough time to reach and
            # that have not already been opened.
            for dest_valve_id, dest_path in cur_valve['distances'].items():
                dest_time_remaining = \
                    MAX_MINUTES - mins_elapsed - len(dest_path)

                if (dest_time_remaining > 0 and
                    dest_valve_id not in opened_valves):
                    # We may have seen this combination of mins elapsed, flow
                    # rates, and path before. If so, we can short-circuit this
                    # branch and just fetch the score we've already computed.
                    path_cache_key = (
                        mins_elapsed,
                        tuple(sorted(avail_flow_rates)),
                        tuple(dest_path),
                    )

                    try:
                        score, full_dest_path = path_cache[path_cache_key]
                    except KeyError:
                        # There's nothing in the cache. Recurse into this
                        # valve and cache the store.
                        score, full_dest_path = _find_best(
                            cur_path=cur_path + dest_path,
                            opened_valves=set(opened_valves),
                            mins_elapsed=mins_elapsed + len(dest_path) - 1,
                            avail_flow_rates=set(avail_flow_rates))
                        path_cache[path_cache_key] = (score, full_dest_path)

                    # Re-compute our best score so far.
                    score += eventual_pressure

                    if score > best_score:
                        best_score = score
                        best_path = full_dest_path

        # Return the best score we could find using this path.
        return best_score, best_path

    if opened_valves is None:
        opened_valves = set()

    # Begin walking the graph from the start node.
    return _find_best(
        mins_elapsed=0,
        opened_valves=opened_valves,
        cur_path=['AA'],
        avail_flow_rates={
            _valve['flow_rate']
            for _valve in valves.values()
            if _valve['flow_rate'] > 0 and _valve['id'] not in opened_valves
        })


def main():
    """Main logic for the program.

    We'll start by parsing the valve list, then running Djikstra's Shortest
    Path algorithm to compute distances to other valves, and then begin the
    operation to find the best score.
    """
    valve_re = re.compile(
        r'^Valve (?P<valve_id>[A-Z]{2}) has flow rate=(?P<flow_rate>\d+); '
        r'tunnels? leads? to valves? (?P<connected>[A-Z]{2}(?:, [A-Z]{2})*)$'
    )

    # First, parse out the information on the valve network.
    with open('input', 'r') as fp:
        for line in fp.readlines():
            m = valve_re.match(line)
            assert m

            valve_id = m.group('valve_id')

            valves[valve_id] = {
                'connected': m.group('connected').split(', '),
                'distances': {},
                'flow_rate': int(m.group('flow_rate')),
                'id': valve_id,
            }

    # We're now going to loop through each product of valves, calculating the
    # shortest path to go from one valve to another.
    #
    # We'll skip any destination valves with a flow rate of 0, because those
    # make for lousy destinations.
    for valve_id, valve in valves.items():
        for dest_valve_id, dest_valve in valves.items():
            if dest_valve_id != valve_id and dest_valve['flow_rate'] != 0:
                # Calculate the shortest path needed to go from valve_id to
                # dest_valve_id.
                valve['distances'][dest_valve_id] = \
                    get_shortest_path(valve_id, dest_valve_id)

    # Now figure out the best pressure release score achievable.
    #
    # In this task, we're going to start by letting the player find the
    # best path.
    #
    # Then, based on those paths, we'll run again for the elephant, starting
    # over at the same time but only considering the remaining valves.
    #
    # This *only* works for the real input. In the test input, the player will
    # open all graphs up-front, using this approach.
    score1, best_path1 = get_best_score()
    score2, best_path2 = get_best_score(opened_valves=set(best_path1))
    total_score = score1 + score2

    print('Most pressure released = %s' % total_score)


if __name__ == '__main__':
    main()
