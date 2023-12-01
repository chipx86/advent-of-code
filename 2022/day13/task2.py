#!/usr/bin/env python3
#
# Task 2 is similar to Task 1 (see task1.py), but in this task, we don't just
# need to check if two pairs are in order. We need to sort through all
# packets (nested lists), along with two special "divider packets", and place
# them in the right order.
#
# This means turning our are_lists_in_order() into a sort comparator function.
#
# To do that, we'll be changing the results from (True, False, None) to
# (-1, 0, 1). This is pretty common for sort comparators. If you know C,
# Think strcmp() and friends.
#
# So the logic doesn't change. Just the return types. And I could easily go
# back and use those in task1.py, but I didn't know it'd be used for sorting
# in this way, so I had no reason to design its interface around that then.

from functools import cmp_to_key


def parse_list(list_str):
    """Parse a potentially-nested list of integers.

    This will manually parse the list, tracking the nesting levels, providing
    validation, and ensuring we're properly converted single- or multi-digit
    string-encoded numbers to integers.

    In Python, this could easily be replaced with a call to
    :py:func:`ast.literal_eval`, but I want to show how you could build this
    yourself.

    This will call itself recursively for any sub-list.

    Args:
        list_str (str):
            The string-encoded list to parse.

    Returns:
        list:
        The parsed list.
    """
    assert list_str

    # We're going to start off with a list. This won't be the top-level list.
    # Rather, it'll be a container for the top-level list. This will make the
    # logic below just a bit easier (no special-casing of "What if the current
    # list is None?).
    cur_list = []
    lists_stack = [cur_list]

    i = 0

    # We're going to walk through the string. Each bit of parsing logic below
    # may advance the current character index (i) by as much as it wants.
    # That's why we're not just iterating over the list.
    while i < len(list_str):
        c = list_str[i]

        if c == '[':
            # This is the beginning of a new sub-list (or the main list).
            # Build it, put it on the stack, and append to the current list.
            new_list = []
            lists_stack.append(new_list)
            cur_list.append(new_list)

            cur_list = new_list
            i += 1
        elif c == ']':
            # This is the end of a list. Pop it off the stack and set the
            # current list to the parent (which may now be the top-most
            # container list, if we're done with the input).
            lists_stack.pop()
            cur_list = lists_stack[-1]
            i += 1
        elif c == ',':
            # This is a delimiter between lists. There's nothing to do here
            # but advance the character index.
            i += 1
        else:
            # We should be in a number. We'll keep scanning until we get
            # something that is not a digit (updating the character index
            # as we go), and then convert the result into an integer.
            assert c.isdigit()

            item_str = ''

            while list_str[i].isdigit():
                item_str += list_str[i]
                i += 1

            cur_list.append(int(item_str))

    # By now, cur_list is our container list again. Grab the top-level list out
    # of it.
    return cur_list[0]


def are_lists_in_order(list1, list2, indent=''):
    # First, make sure the lists have the same number of items. If not, the
    # test failed.
    print('%s- Compare %r vs %r' % (indent, list1, list2))
    indent += '  '

    for item1, item2 in zip(list1, list2):
        # First, normalize our pairs so that they're either both integers or
        # lists, as per instructions in the task.
        #
        # We're going to avoid more than one isinstance check, due to the
        # expense. (It's actually very small, but I don't like unnecessary
        # repeat calls.)
        item1_is_list = isinstance(item1, list)
        item2_is_list = isinstance(item2, list)

        if item1_is_list != item2_is_list:
            if item1_is_list and not item2_is_list:
                print('%s- Mixed types; convert right to [%r] and retry'
                      % (indent, item2))
                item2 = [item2]
                item2_is_list = True
            elif item2_is_list and not item1_is_list:
                print('%s- Mixed types; convert left to [%r] and retry'
                      % (indent, item1))
                item1 = [item1]
                item1_is_list = True

        if item1_is_list:
            assert item2_is_list

            result = are_lists_in_order(item1, item2, indent + '  ')

            if result != 0:
                # We have a definitive result, so return it.
                return result
        else:
            assert isinstance(item1, int)
            assert isinstance(item2, int)

            print('%s- Compare %s vs %s' % (indent, item1, item2))

            if item1 < item2:
                # "If the left integer is lower than the right integer, the
                # inputs are in the right order"
                print('%s  - Left side is smaller, so inputs ARE in the right '
                      'order'
                      % indent)
                return -1
            elif item1 > item2:
                # "If the left integer is higher than the right integer, the
                # inputs are not in the right order"
                print('%s  - Right side is smaller, so inputs ARE NOT in the '
                      'right order'
                      % indent)
                return 1
            else:
                # Otherwise, the inputs are the same integer; continue checking
                # the next part of the input.
                pass

    # We've gone through the whole list, and nothing was out of order!
    #
    # Or... is it? We need to see if we ran out of items in one list or
    # another before returning a definitive result (or None, to continue on).
    if len(list1) > len(list2):
        print('%s- Right side ran out of items, so inputs ARE NOT in order (2)'
              % indent)
        return 1
    elif len(list1) < len(list2):
        print('%s- Left side ran out of items, so inputs ARE in order (2)'
              % indent)
        return -1

    return 0


def iter_packets(fp):
    """Iterate through all packets in a file.

    This will take care to strip packets and ignore blank lines.

    Args:
        fp (io.FileIO):
            The file pointer to read from.

    Yields:
        list:
        Each packet in the file.
    """
    while True:
        packet = fp.readline()

        if packet == '':
            # There are no more packets left to read.
            break

        packet = packet.strip()

        if packet:
            # This is not a blank line.
            yield parse_list(packet)


pair_num = 1
pairs_in_order_sum = 0


with open('input', 'r') as fp:
    # Read in the packets, and mix in our two divider packets. We want to
    # sort these in order, using are_lists_in_order as a comparator function.
    packets = sorted(
        [
            [[2]],
            [[6]],
        ] + list(iter_packets(fp)),
        key=cmp_to_key(are_lists_in_order))

    # We'll dedicate variables and a counter for these packets.
    #
    # I'm going this route because I want to very efficiently be able to tell
    # when I'm done scanning (using the dividers_found counter) and to have
    # a dedicated place to store those indexes.
    divider2_i = None
    divider6_i = None
    dividers_found = 0

    # Find the indexes of the divider packets.
    for i, p in enumerate(packets, start=1):
        if divider2_i is None and p == [[2]]:
            divider2_i = i
            dividers_found += 1
        elif divider6_i is None and p == [[6]]:
            divider6_i = i
            dividers_found += 1

        if dividers_found == 2:
            # We found all the dividers.
            break

    # We found them. Now we can multiply to get the decoder key.
    decoder_key = divider2_i * divider6_i

    print(f'Decoder key = {decoder_key}')
