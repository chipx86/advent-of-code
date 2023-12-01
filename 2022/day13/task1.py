#!/usr/bin/env python3
#
# In today's task, we have to go through pairs of nested lists and see if they
# are in the right order.
#
# But first, we have to parse them. Now, in Python, we have this lovely
# ast.literal_eval() function that can safely parse through Python native
# types, like lists of integers, and give a result. This happens to work well
# with our task's input.
#
# But that's no fun. And despite wanting to go for performance, I decided to
# implement this myself. It might be helpful to others.
#
# Once we have those parsed pairs, we can compare them. This is done through a
# set of rules:
#
# 1. When comparing a list to an integer, convert the integer into a list.
#
# 2. When comparing lists to lists:
#
#    1. Re-run the comparison for the two lists. If we get a definitive result,
#       we're done, and can bubble that up.
#
# 3. When comparing integers to integers:
#
#    1. If integer1 < integer2, we have a definitive result of True. Bubble it
#       up.
#
#    2. If integer1 > integer1, we have a definitive result of False. Bubble it
#       up.
#
#    3. If integer1 == integer2, continue on with the next value.
#
# 4. If we finished processing a list, and one of the two lists still has
#    items remaining:
#
#    1. If list1 has items left, return a definitive result of True. Bubble it
#       up.
#
#    2. If list2 has items left, return a definitive result of False. Bubble it
#       up.
#
#    3. Otherwise, return None, to let the parent continue on.
#
#    (This part of the comparison is roughly equivalent to comparing integers.)
#
# Once we're done with all that mess, we just need to get the sum of 1-based
# pair IDs that were in order and output the result.

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
    """Return whether two lists are in order.

    This will return True if the two lists are in order, False if they are not,
    or None if no determination could be made.

    This will be called recursively for sub-lists.

    This will also emit some debug output, so you can all follow along at home.

    Args:
        list1 (list):
            The first list to compare.

        list2 (list):
            The second list to compare.

        indent (str, optional):
            An indentation marker, to help with debugging output for recursive
            calls.

    Returns:
        bool:
        ``True`` if the two lists are in order.

        ``False`` if they are not in order.

        ``None`` if a determination could not be made (they are equal).
    """
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

            if result is not None:
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
                return True
            elif item1 > item2:
                # "If the left integer is higher than the right integer, the
                # inputs are not in the right order"
                print('%s  - Right side is smaller, so inputs ARE NOT in the '
                      'right order'
                      % indent)
                return False
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
        return False
    elif len(list1) < len(list2):
        print('%s- Left side ran out of items, so inputs ARE in order (2)'
              % indent)
        return True

    return None


pair_num = 1
pairs_in_order_sum = 0


# We can now read through the file input, checking which pairs are in order,
# and calculating a sum for the answer.
with open('input', 'r') as fp:
    while True:
        pair1 = fp.readline()
        pair2 = fp.readline()

        assert pair1
        assert pair2

        items1 = parse_list(pair1.strip())
        items2 = parse_list(pair2.strip())

        if are_lists_in_order(items1, items2):
            pairs_in_order_sum += pair_num

        print()

        # There should be a blank line here. If not, we're done.
        if fp.readline() == '':
            break

        pair_num += 1


print(f'Sum of indices of pairs in order = {pairs_in_order_sum}')
