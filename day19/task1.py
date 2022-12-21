#!/usr/bin/env python3
#
# I liked the concept of this task, but it drove me a bit insane. I'm also
# perhaps getting burnt out on these.
#
# For this task, we have a series of blueprints and need to find the largest
# number of geodes we can effectively mine, based on the optimal order and
# times in which robots are built. Each robot takes a certain quantity of
# types of resources (based on the blueprint), and we start with one robot
# that can mine ore (the common resource).
#
# For this, I opted for a recursive solution. We know our max depth (24 --
# MAX_MINUTES), and that's safe enough.
#
# At each tick (call), we compute the number of resources we'll be mining,
# figure out which robots we may want to build, and test each one in a new
# path recursively, with a copy of our state.
#
# The path with the highest score wins.
#
# This would take a while, so there's a few shortcuts I employ:
#
# 1. I never build more robots than we need. That's defined by the total cost
#    of resources required for the next robot up. So if geode robots require
#    10 obsidian, we max out at 10 obsidian robots (anything more is a waste
#    of resources, given our time).
#
# 2. If we're on a branch that hasn't build a geode robot yet, and we've
#    exceeded the time taken to build one from another branch, consider this
#    branch a failure and prune it.
#
# 3. Same with obsidian, but allow for obsidan robots to be built one tick
#    late. (Is this a hack? I dunno, it works for all tests in my input.)
#
# 4. Branches are cached. If we explore a branch we've already explored before,
#    given the number of mining robots, resources, time elapsed, and pending
#    robot to build, then we bail.
#
# Each of these saves a fair amount of time, taking this from minutes to
# seconds. I know there are other optimizations that can be made, and have
# experimented with "how many geode robots can be effectively build / geodes
# we can effectively mine in time?", but hit some issues and decided not to
# spend too much time on it.

import re
import sys


# The maximum number of minutes we have to build robots and collect geodes.
MAX_MINUTES = 24


def get_quality_level(blueprint):
    """Return the quality level from mining geodes.

    This attempts to recursively walk through branches of possible bots,
    determining which order bots should be built in order to get to geode
    mining the fastest.

    For this, we attempt to both prune and cache branches using a number of
    approaches, as documented up above.

    Args:
        blueprint (dict):
            The blueprint being tested.

    Returns:
        int:
        The resulting quality level of the blueprint.
    """
    robots = blueprint['robots']

    # The earliest mins_elapsed values at which geodes and obsidian have been
    # built.
    earliest_geode = sys.maxsize
    earliest_obsidian = sys.maxsize

    # Our cache for paths, keyed off with enough information available to
    # reliably prune the bath.
    seen_paths = {}

    # We don't need to build as many robots as possible. There's a limit to
    # what's useful. We're capping that at the maximum number of resources
    # used to build a robot.
    max_robots = {
        'clay': robots['obsidian']['costs']['clay'],
        'geode': sys.maxsize,
        'obsidian': robots['geode']['costs']['obsidian'],
        'ore': max(robots['clay']['costs']['ore'],
                   robots['obsidian']['costs']['ore'],
                   robots['geode']['costs']['ore']),
    }

    def _get_best(*, mins_elapsed, inventory, active_robots):
        nonlocal earliest_geode
        nonlocal earliest_obsidian

        if mins_elapsed >= MAX_MINUTES:
            # We've exceeded our time. Return what we've collected so far.
            return inventory['geode']

        # Have the robots collect ore.
        #
        # This will be equal to the number of robots we have at this stage.
        new_resources = active_robots.copy()

        # Get a list of all robots currently buildable.
        #
        # We'll avoid building more than our cap.
        buildable_robots = {
            robot_id: robot
            for robot_id, robot in blueprint['robots'].items()
            if active_robots[robot_id] + 1 <= max_robots[robot_id] and all(
                inventory[resource] >= cost
                for resource, cost in robot['costs'].items()
            )
        }

        # Figure out our priorities.
        #
        # If we can build a geode robot, we *always* want to build one.
        #
        # If we can't, but we can build an obsidian robot, then we *always*
        # want to build one.
        #
        # We don't apply this logic for clay, because otherwise we just use
        # up all our ore at every opportunity.
        if 'geode' in buildable_robots:
            candidates = ['geode']
            earliest_geode = min(earliest_geode, mins_elapsed)
        elif 'obsidian' in buildable_robots:
            candidates = ['obsidian']
            earliest_obsidian = min(earliest_obsidian, mins_elapsed)
        else:
            candidates = list(buildable_robots.keys()) + [None]

        # Check if we're behind schedule for geode production, or if we're
        # about to be behind schedule for obsidian production. We give a bit
        # more leeway with the obsidian robots.
        #
        # If we're behind, bail. This speeds things up considerably. Especially
        # the obsidian check.
        if ((mins_elapsed > earliest_geode and active_robots['geode'] == 0) or
            (mins_elapsed > earliest_obsidian + 1 and
             active_robots['obsidian'] == 0)):
            return None

        # Process the next step, and maybe build some robots. We'll do this
        # recursively, try to figure out the optimal score.
        best_score = inventory['geode'] + new_resources['geode']

        # Test each candidate.
        for robot_id in candidates:
            # We'll cache our path states, in an effort to avoid calculating
            # possible outcomes of branches when possible.
            key = (
                mins_elapsed,
                tuple(inventory.items()),
                tuple(active_robots.items()),
                robot_id,
            )

            try:
                score, new_inventory = seen_paths[key]
            except KeyError:
                # This is our first time in this path. We're going to create
                # a copy of our inventory and active robots for this branch
                # simulation.
                #
                # We'll also build our robots and consume our costs at this
                # point, since we're simulating the robot production now.
                new_inventory = inventory.copy()
                new_active_robots = active_robots.copy()

                if robot_id is not None:
                    # Build the robot. Consume the resources needed.
                    for resource, cost in robots[robot_id]['costs'].items():
                        if cost > 0:
                            new_inventory[resource] -= cost

                    new_active_robots[robot_id] += 1

                # Robots mine resources *after* we build new robots. Go ahead
                # and add to our inventory now.
                for resource, value in new_resources.items():
                    new_inventory[resource] += value

                # Now we can test this branch, see if we get a useful score.
                score = _get_best(mins_elapsed=mins_elapsed + 1,
                                  inventory=new_inventory,
                                  active_robots=new_active_robots)
                seen_paths[key] = (score, new_inventory)

            if score is not None and score > best_score:
                # We found the best branch! Return the score.
                best_score = score

        return best_score

    geodes_opened = _get_best(
        mins_elapsed=0,
        inventory={
            'clay': 0,
            'geode': 0,
            'obsidian': 0,
            'ore': 0,
        },
        active_robots={
            'clay': 0,
            'geode': 0,
            'obsidian': 0,
            'ore': 1,
        })

    quality_level = geodes_opened * blueprint['id']

    print('Blueprint %s geodes opened = %s. Quality level = %s'
          % (blueprint['id'], geodes_opened, quality_level))

    return quality_level


def main():
    """Run the program for day 19 task 1.

    This will read the blueprints and compute a quality score for each.

    Once all blueprints have been processed, the total quality level will be
    displayed.
    """
    BLUEPRINT_RE = re.compile(
        r'Blueprint (?P<blueprint_id>\d+): '
        r'Each ore robot costs (?P<ore_robot_ore_cost>\d+) ore\. '
        r'Each clay robot costs (?P<clay_robot_ore_cost>\d+) ore\. '
        r'Each obsidian robot costs (?P<obsidian_robot_ore_cost>\d+) ore and '
        r'(?P<obsidian_robot_clay_cost>\d+) clay\. '
        r'Each geode robot costs (?P<geode_robot_ore_cost>\d+) ore and '
        r'(?P<geode_robot_obsidian_cost>\d+) obsidian\.'
    )

    total_quality_level = 0

    with open('input', 'r') as fp:
        for blueprint_id, line in enumerate(fp.readlines(), start=1):
            m = BLUEPRINT_RE.match(line)
            assert m

            group = m.groupdict()

            blueprint = {
                'id': blueprint_id,
                'robots': {
                    robot_id: {
                        'id': robot_id,
                        'costs': {
                            resource: int(
                                group.get(f'{robot_id}_robot_{resource}_cost',
                                          0)
                            )
                            for resource in ('clay', 'obsidian', 'ore')
                        },
                    }
                    for robot_id in ('clay', 'geode', 'obsidian', 'ore')
                },
            }

            print('======= BLUEPRINT %s ========' % blueprint_id)

            total_quality_level += get_quality_level(blueprint)

            print()

    print('Total quality level = %s' % total_quality_level)


if __name__ == '__main__':
    main()
