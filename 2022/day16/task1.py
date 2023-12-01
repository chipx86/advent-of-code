#!/usr/bin/env python3
#
# In today's task, we're stuck in an active volcano with a bunch of elephants,
# centered around the Steam Pipe Trunk Distribution Venue, trying to figure out
# the optimal path through tunnels to release steam pipes.
#
# As one does.
#
# Basically, there's a series of rooms. Some lead to other rooms. All have
# valves, but some would release 0 flow rate (so, no point in opening a valve
# there). The rest have varying degrees of flow rate.
#
# We have 30 minutes before the volcano erupts. Each minute, we can spend one
# action: Walking, or opening a valve. Each minute that ticks away reduces the
# total pressure that would be released from a valve by the end of 30 minutes.
#
#     total_eventual_pressure = minutes_remaining * flow_rate
#
# This and task2 are both about graph theory concepts. Outside of some stuff
# like topological sorts for dependency graphs, I've had very little working
# experience with most of graph theory, and as such I got stuck on this for a
# while with some pretty inefficient attempts. I ended up working through the
# problem, though, especially after realizing that Djikstra's shortest-path
# algorithm (used in Day 12) was probably going to help me out here.
#
# So here's the plan of attack:
#
# 1. Build a graph of all the valves, their flow rates, and where they connect
#    connect (this is directional).
#
# 2. For each valve, using Djikstra's Shortest Path algorithm, build up a
#    mapping of all destination valves with a flow rate (anything worth moving
#    toward), and calculate the path to get there.
#
# 3. Generate a plan for walking through the graph and opening valves in the
#    most optimal way (at least, in terms of my implementation).
#
# Now, here's where my knowledge of graph theory algorithms break down. I'm
# sure there's a really clever way of walking through the graph with absolute
# time taken, but I don't know it (and I'm trying to implement these based on
# my own abilities).
#
# So, for figuring out the best route, we're doing this for each valve
# (starting at "AA"):
#
# 1. For the current valve, check if it can be opened (has a flow rate > 0 and
#    hasn't been opened yet).
#
#    If so, we open it, add 2 minutes to the time elapsed (traversal + open
#    actions), and add the score to the candidates for best score on this path.
#
#    If it can't be opened, we don't open it, and we only had 1 minute (for
#    traversal), and a 0 score to the candidates.
#
# 2. Perform a quick check to make sure we haven't now ran out of time and that
#    there's still valves open. If we're good to continue on.
#
#    We'll now loop through each unopened valve we can reach and make sure we
#    have time to reach it from the current path.
#
#    If so, run it through the steps above and get a score. Store the best of
#    the current score and this one.
#
# 3. The resulting score wins for that valve.
#
# This is where I know there's some optimizations that I could put in. This
# isn't *slow*. Execution time is < 1 second (~350ms here), but still, it could
# be faster. I've tried to do a "best of" check as I process candidates, to try
# to bail early, but then I miss good paths.
#
# There are a couple optimizations, though:
#
# 1. I employ a path cache to avoid recursing down branches that have been
#    seen before in other iterations. This is keyed off by:
#
#        (mins_elapsed, avail_flow_rates, path)
#
#    This chops down the number of branches explored by a whopping 47%! That's
#    branches 65,838 branches cut off the search time.
#
# 2. I never explore sub-branches if there isn't enough time to complete them.
#
# I'm sure there's plenty of other ways to go about this, but it's fast, it
# works, and I can look at the code and reason about it. Good enough.

import re


# The maximum number of minutes in which actions can be taken.
#
# For task 1, we get the full 30 minutes.
MAX_MINUTES = 30


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


def get_best_score():
    """Return the best pressure relief score available.

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
                        score = path_cache[path_cache_key]
                    except KeyError:
                        # There's nothing in the cache. Recurse into this
                        # valve and cache the store.
                        score = _find_best(
                            cur_path=cur_path + dest_path,
                            opened_valves=set(opened_valves),
                            mins_elapsed=mins_elapsed + len(dest_path) - 1,
                            avail_flow_rates=set(avail_flow_rates))
                        path_cache[path_cache_key] = score

                    # Re-compute our best score so far.
                    best_score = max(best_score, eventual_pressure + score)

        # Return the best score we could find using this path.
        return best_score

    # Begin walking the graph from the start node.
    return _find_best(
        mins_elapsed=0,
        opened_valves=set(),
        cur_path=['AA'],
        avail_flow_rates={
            _valve['flow_rate']
            for _valve in valves.values()
            if _valve['flow_rate'] > 0
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

    # Now figure out the best pressure release score achievable. Details for
    # this are up above.
    total_score = get_best_score()

    print('Most pressure released = %s' % total_score)


if __name__ == '__main__':
    main()
