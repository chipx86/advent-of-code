#!/usr/bin/env python3
#
# This task involves loading in a set of instructions having to do with
# "monkeys", lists of items, and throwing them to other monkeys.
#
# It's like a very purpose-built programming language, or domain-specific
# language, for state management and conditionals involving the movement of
# items.
#
# Each monkey has:
#
# 1. An ID (referenced by other monkeys)
# 2. A starting list of items (each being represented as a "worry level"
#    integer).
# 3. An operation to perform on a value for each item.
# 4. A test expression to see if an item/worry level is divisible by some
#    number.
# 5. What monkey to throw to, based on whether the test expression results
#    in a truthy or falsy value.
# 6. A counter for how many items have been processed.
#
# Each round, each monkey gets a turn in order. Each turn, the monkey processes
# each item in its list one-by-one. The item's worry level is divided by 3,
# and then the operation is performed on it, mutating the worry level further.
# That result is then tested, and then thrown to a monkey based on that value.
#
# I took a sort of general approach to this one, rather than minimalistic.
# I have classes representing items, operations, test expressions, and throw
# commands. In theory, this could all be extended to support more variations
# on all this. Certainly, this could be designed in a far more compact way
# for this particular task.
#
# First, we parse all data from the file, asserting our parsing is exactly
# what we expect.
#
# Then we run through each round, and each monkey in order, following the
# rules up above.
#
# All the while, we're calculating the total list of processed items.
#
# Once all that is done, we get the monkeys with the two highest item processed
# counters, multiply those, and that is the answer.

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

        self.value1 = value1
        self.op = op
        self.value2 = value2

        if self.op == '+':
            self.op_func = int.__add__
        elif self.op == '*':
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
        if self.value1 == 'old':
            value1 = old
        else:
            value1 = int(self.value1)

        if self.value2 == 'old':
            value2 = old
        else:
            value2 = int(self.value2)

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

        # Track how many items are being inspected.
        self.inspect_count += len(self.items)

        # For each item, figure out new worry levels and what needs to be
        # done based on the worry level of the item.
        for item in self.items:
            worry_level = int(operation.apply(item.worry_level) / 3)
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
ROUNDS = 20


# The list of monkeys.
#
# Indices correspond to monkey IDs.
monkeys = []


with open('input', 'r') as fp:
    while True:
        monkey = Monkey.read(fp)
        assert monkey.id == len(monkeys)

        monkeys.append(monkey)

        if fp.readline() == '':
            # We've parsed the end of the file.
            break

    # As per the instructions, we'll be performing 20 rounds. We want to know
    # the two most active monkeys (defined as how many items they inspect).
    for i in range(ROUNDS):
        for monkey in monkeys:
            monkey.run()

    # We can now find the top two monkeys.
    max_inspection_counts = sorted(
        [
            monkey.inspect_count
            for monkey in monkeys
        ],
        reverse=True)[:2]

    print('Level of monkey business = %s'
          % (max_inspection_counts[0] * max_inspection_counts[1]))
