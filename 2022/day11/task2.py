#!/usr/bin/env python3
#
# This task involves loading in a set of instructions having to do with
# "monkeys", lists of items, and throwing them to other monkeys.
#
# It's very much like task1.py (read that for details), with one major
# constraint: The worry level is capable of growing to unreasonably-high
# numbers.
#
# This is partly due to the number of rounds (10,000 now), and partly due
# to the removal of the code that divides the worry level by 3.
#
# The task forces us to solve this. It sounds like there are a lot of options
# out there. I *think* mine is the best of the choices.
#
# Basically, we need the number to be capped to something, so it doesn't
# grow out of control. But we can affect the test expressions, which all
# check if the number is divisible by something.
#
# The approach I use is to store a value we can apply a mod operation to
# (dividing by this and using the remainder as the new value).
#
# Let me walk you through this:
#
# Say we had one monkey and it checks if the value is divisible by 3. Watch
# what happens when we apply a mod of 3:
#
#     0 % 3 == 0
#     1 % 3 == 1
#     2 % 3 == 2
#     3 % 3 == 0  (we've now reset)
#
# Even if we alter the value through some kind of math, the divisor will get
# us a suitable value we can use here. We'll test with a test expression using
# a divisor of 11:
#
#     Without the mod:
#         maths: (42 / 3 + 19) == 33
#         test: 33 % 11 == 0 (true)
#
#     With the mod on each calculation:
#         maths: (42 / 3) % 11 == 3
#                (3 + 19) % 11 == 0
#         test: 0 % 11 == 0 (true)
#
# We're dealing with multiple divisors, and need to support them all. To do
# this, we multiply all of them together. So let's run through that. We'll
# choose divisors 3 and 7, getting us a worry_level_mod of 21 (3 * 7).
#
#     Without the mod:
#         maths: (40 / 5 * 22 - 8) == 84
#         test1: 84 % 3 == 0 (true)
#         test2: 84 % 7 == 0 (true)
#
#     With the mod on each calculation:
#         maths: (40 / 5) % 21 == 8
#                (8 * 12) % 21 == 8
#                (8 - 8) % 21 == 0
#         test1: 0 % 3 == 0 (true)
#         test2: 0 % 7 == 0 (true)
#
# One more to prove it, with a result that doesn't end in 0 (requiring all
# divisors to have some common value that they can be divided by). We'll use
# 4 and 8 (worry_level_mod = 32):
#
#     Without the mod:
#         maths: (16 * 8 + 16) == 240
#         test1: 240 % 4 == 0 (true)
#         test2: 240 % 8 == 0 (true)
#
#     With the mod on each calculation:
#         maths: (16 * 8) % 32 == 0
#                (0 + 16) % 32 == 16
#         test1: 16 % 4 == 0 (true)
#         test2: 16 % 8 == 0 (true)
#
# NOTE: This only works if all division ends up being integer division.
#       Any non-integer results, and it all breaks down. But this works for
#       the tasks.

import re


class Item:
    """An item held by a monkey.

    This is represented by a worry level. This could be an integer, but I'm
    modelling this with the worry level as a property.
    """

    def __init__(self, worry_level):
        """Initialize the item.

        Args:
            worry_level (int):
                The worry level of this item.
        """
        self.worry_level = worry_level


class Operation:
    """An operation to perform to update an item's worry level.

    Operations are pretty basic. In these tasks, it will always apply either
    a "+" or a "*" to two values, both of which may be variables or integers.
    """

    OPERATION_RE = re.compile(
        r'new = (?P<value1>old|\d+) (?P<op>[\+\*]) (?P<value2>old|\d+)')

    @classmethod
    def from_string(cls, operation_str):
        """Parse an operation from a string.

        This will construct a new Operation based on the expression in the
        string.

        Args:
            operation_str (str):
                The operation string to parse.

        Returns:
            Operation:
            The parsed operation.
        """
        # The input is pretty basic, so we don't need to allow for much
        # variance here.
        m = cls.OPERATION_RE.match(operation_str)
        assert m

        return cls(value1=m.group('value1'),
                   op=m.group('op'),
                   value2=m.group('value2'))

    def __init__(self, value1, op, value2):
        """Initialize the operation.

        Args:
            value1 (str):
                A string for the first value. This will either be a variable
                ("old") or a number (as a string).

            op (str):
                The operator to apply. This will either be "+" or "*".

            value2 (str):
                A string for the second value. This will either be a variable
                ("old") or a number (as a string).
        """
        assert op in ('+', '*')

        try:
            self.value1 = int(value1)
        except ValueError:
            # This is a variable.
            self.value1 = value1

        try:
            self.value2 = int(value2)
        except ValueError:
            # This is a variable.
            self.value2 = value2

        if op == '+':
            self.op_func = int.__add__
        elif op == '*':
            self.op_func = int.__mul__

    def apply(self, old):
        """Apply the operation and return the resulting value.

        This will add or multiply the values, taking in an "old" value to use
        for variables, and return a result.

        Args:
            old (int):
                The old value to use for "old" variables.

        Returns:
            int:
            The resulting value.
        """
        value1 = self.value1
        value2 = self.value2

        if value1 == 'old':
            value1 = old

        if value2 == 'old':
            value2 = old

        return self.op_func(value1, value2)


class TestExpression:
    """An expression used to test a value.

    This will only test if a value is divisible by another value.
    """

    EXPRESSION_RE = re.compile(r'divisible by (?P<value>\d+)')

    @classmethod
    def from_string(cls, expression_str):
        """Parse a test expression from a string.

        This will construct a new TestExpression based on the expression in the
        string.

        Args:
            expression_str (str):
                The expression string to parse.

        Returns:
            TestExpression:
            The parsed test expression.
        """
        # The input is pretty basic, so we don't need to allow for much
        # variance here.
        m = cls.EXPRESSION_RE.match(expression_str)
        assert m

        return cls(divisor=int(m.group('value')))

    def __init__(self, divisor):
        """Initialize the test expression.

        Args:
            divisor (int):
                The divisor found in the test expression.
        """
        self.divisor = divisor

    def test(self, value):
        """Return whether a value passes the test.

        Args:
            value (int):
                The value to test.

        Returns:
            bool:
            ``True`` if the expression passed. ``False`` if it did not.
        """
        return value % self.divisor == 0


class ThrowCommand:
    """A command to throw an item to another monkey.

    When run, this will place an item at the end of a recipient monkey's list.
    """

    THROW_RE = re.compile(r'throw to monkey (?P<monkey>\d+)')

    @classmethod
    def from_string(cls, command_str):
        """Parse a throw command from a string.

        This will construct a new ThrowCommand based on the statement in the
        string.

        Args:
            command_str (str):
                The command string to parse.

        Returns:
            ThrowCommand:
            The parsed command.
        """
        # The input is pretty basic, so we don't need to allow for much
        # variance here.
        m = cls.THROW_RE.match(command_str)
        assert m

        return cls(throw_to_monkey_id=int(m.group('monkey')))

    def __init__(self, throw_to_monkey_id):
        """Initialize the command.

        Args:
            throw_to_monkey_id (int):
                The ID of the monkey to throw to.
        """
        self.throw_to_monkey_id = throw_to_monkey_id

    def run(self, item):
        """Run the command.

        Args:
            item (Item):
                The item to throw.
        """
        monkeys[self.throw_to_monkey_id].items.append(item)


class Monkey:
    """A representation of a monkey.

    This will take care of all state storage for a monkey, and running through
    a monkey's phase each turn.
    """

    MONKEY_ID_RE = re.compile(r'^Monkey (?P<monkey_id>\d+):')

    @classmethod
    def read(cls, fp):
        """Return a monkey based on file input.

        Args:
            fp (io.FileIO):
                The file pointer to read from.

        Returns:
            Monkey:
            The parsed monkey.
        """
        line = fp.readline().rstrip()
        m = cls.MONKEY_ID_RE.match(line)
        assert m

        monkey_id = int(m.group('monkey_id'))
        starting_items = [
            Item(worry_level=int(_item))
            for _item in cls._read_keyval(fp, 'Starting items').split(', ')
        ]
        operation = Operation.from_string(cls._read_keyval(fp, 'Operation'))
        test_expression = TestExpression.from_string(cls._read_keyval(fp,
                                                                      'Test'))
        if_true = ThrowCommand.from_string(cls._read_keyval(fp, 'If true'))
        if_false = ThrowCommand.from_string(cls._read_keyval(fp, 'If false'))

        return cls(monkey_id=monkey_id,
                   starting_items=starting_items,
                   operation=operation,
                   test_expression=test_expression,
                   if_true=if_true,
                   if_false=if_false)

    @classmethod
    def _read_keyval(self, fp, key):
        """Read a key/value pair from file input.

        This ignores indentation levels in the file input, and consumes the
        line. It also expects that the key matches the line.

        Args:
            fp (io.FileIO):
                The file pointer to read from.

            key (str):
                The key to read.

        Returns:
            str:
            The value corresponding to the key on that line.
        """
        prefix = f'{key}: '

        line = fp.readline().strip()
        assert line.startswith(prefix)

        return line[len(prefix):]

    def __init__(self, monkey_id, starting_items, operation, test_expression,
                 if_true, if_false):
        """Initialize the monkey.

        Args:
            monkey_id (int):
                The ID of the monkey.

            starting_items (list of Item):
                The list of items initially held by the monkey.

            operation (Operation):
                The operation to perform on each item in the monkey's turn.

            test_expression (TestExpression):
                The expression used to test each item.

            if_true (ThrowCommand):
                The command to run when the test expression is true.

            if_false (ThrowCommand):
                The command to run when the test expression is false.
        """
        self.id = monkey_id
        self.items = starting_items
        self.operation = operation
        self.test_expression = test_expression
        self.if_true = if_true
        self.if_false = if_false
        self.inspect_count = 0

    def run(self):
        """Run the monkey's instructions for one turn.

        This will loop through each held item, update worry levels, and
        determine which command to run.

        It also tracks the item inspection count, and resets items after the
        turn is done.
        """
        operation = self.operation
        test_expression = self.test_expression
        if_true = self.if_true
        if_false = self.if_false

        items = self.items

        # Track how many items are being inspected.
        self.inspect_count += len(items)

        # For each item, figure out new worry levels and what needs to be
        # done based on the worry level of the item.
        for item in items:
            worry_level = operation.apply(item.worry_level) % worry_level_mod
            print(f'{item.worry_level} => {worry_level}')
            item.worry_level = worry_level

            if test_expression.test(worry_level):
                if_true.run(item)
            else:
                if_false.run(item)

        # We can now reset the list of items, since all of them have been
        # thrown (and, in these tasks, monkeys never keep items or throw to
        # themselves).
        self.items = []


# The number of rounds to run.
ROUNDS = 10_000


# The list of monkeys.
#
# Indices correspond to monkey IDs.
monkeys = []


# A tracker for the divisor used to cap worry levels.
worry_level_mod = 1


with open('input', 'r') as fp:
    while True:
        monkey = Monkey.read(fp)
        assert monkey.id == len(monkeys)

        # During loading, update worry_level_mod. This will be the product
        # of all test expression divisors. We'll apply a
        # `worry_level % worry_level_mod` each time we process an item,
        # capping the value of worry_level to a value that can't grow out
        # of control, while also allowing the divisors to work.
        worry_level_mod *= monkey.test_expression.divisor

        monkeys.append(monkey)

        if fp.readline() == '':
            # We've parsed the end of the file.
            break

    # As per the instructions, we'll be performing 20 rounds. We want to know
    # the two most active monkeys (defined as how many items they inspect).
    #for i in range(ROUNDS):
    for i in range(ROUNDS):
        if i % 100 == 0:
            print('Round %s' % i)

        for monkey in monkeys:
            monkey.run()

    for monkey in monkeys:
        print('Monkey %s inspected items %s times.'
              % (monkey.id, monkey.inspect_count))

    # We can now find the top two monkeys.
    max_inspection_counts = sorted(
        [
            monkey.inspect_count
            for monkey in monkeys
        ],
        reverse=True)[:2]

    print('Level of monkey business = %s'
          % (max_inspection_counts[0] * max_inspection_counts[1]))
