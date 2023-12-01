#!/usr/bin/env python3
#
# This task involves writing a very small assembly language interpreter that
# keeps track of a register (X, which starts at 1) and provides instructions
# (noop, and addx).
#
# noop does nothing, and takes 1 CPU cycle to do that nothing.
#
# addx adds a specific positive or negative integer to X, and takes two CPU
# cycles (only actually adding the value at the end).
#
# So this must track X, CPU cycle counts, and time execution of instructions
# based on how many cycles they take.
#
# To do this, we're keeping track of which instruction we're currently
# operating on and how many cycles remain until executing of that instruction
# is invoked.
#
# When we're at 0 cycles remaining for an instruction (meaning we're jsut
# starting out or our last CPU cycle depleted the "cycles remaining until
# execution" tracking of the instruction), we execute any pending instruction,
# read the next instruction from the file, reset the cycles remaining counter,
# and begin counting down again.
#
# If there are no more instructions to execute, we finish up the cycle and
# end the program.
#
# Also, certain cycles, we're calculating the "signal strength" (cycle count
# multiplied by X) and adding to the existing total. This is done on cycle
# 20, 60, 100, 140, 180, etc. (Note: we start at 20, not 40, but otherwise
# increment by 40).
#
# There's little memory to store, so this program is quite scalable. We process
# instructions from a file as we go, only as needed. No buffering of
# instructions.

def _op_noop():
    """Perform a no-op.

    This doesn't actually do anything.

    This executes 1 cycle after loading.
    """


def _op_addx(value):
    """Add a value to the X register.

    This executes 2 cycles after loading.

    Args:
        value (int):
            The value to add to X.
    """
    registers['X'] += int(value)


def read_instruction(fp):
    """Read an instruction from the file pointer.

    This will read it and parse the instruction name from the values.

    Args:
        fp (io.FileIO):
            The file stream to read from.

    Returns:
        tuple:
        A 2-tuple, featuring:

        Tuple:
            0 (str):
                The instruction name.

            1 (tuple of str):
                A tuple of parameters passed to the instruction.

        If there aren't any instructions left to read, both values will be
        ``None``.
    """
    line = fp.readline().strip()

    if not line:
        return None, None

    parts = line.split(' ')

    return parts[0], tuple(parts[1:])


# The instructions supported by this assembly set.
#
# These map the names to (cycle_count, handler).
OPCODES = {
    'noop': (1, _op_noop),
    'addx': (2, _op_addx),
}


# The registers we're tracking.
#
# This could just be `X`, but I wrote this with a theoretical "we might need
# to support multiple registers!" design.
registers = {
    'X': 1,
}


# Number of cycles we've executed.
cycle_count = 0


# State on the current instruction we're handling.
opcode_handler = None
opcode_cycles_remaining = 0
opcode_values = ()


# Indicates whether we're on the last instruction.
last = False


# Final result we're trying to calculate for the answer.
signal_strength = 0


with open('input', 'r') as fp:
    while not last:
        if opcode_cycles_remaining == 0:
            # Our countdown concluded (or we're on the final instruction).
            # Execute whatever instruction we had read, if any.
            if opcode_handler is not None:
                opcode_handler(*opcode_values)
                opcode_handler = None

            # And now get a new instruction.
            opcode, opcode_values = read_instruction(fp)

            if opcode:
                # We found one, so queue that up for execution and reset the
                # cycle remaining counter.
                opcode_cycles_remaining, opcode_handler = OPCODES[opcode]
            else:
                # There were no more instructions to read. Finish this cycle
                # and then we'll be done.
                last = True

        opcode_cycles_remaining -= 1
        cycle_count += 1

        # Check if we're ready to add to the signal strength for the final
        # answer.
        #
        # We want this on 20 and then every 40 from there (60, 100, 140, etc.).
        # We can subtract 20 and then get the remainder dividing by 40 to see
        # if we're on a 40 count.
        #
        # The math works out such that this is done on at cycles:
        #
        #  20: ((20 - 20) % 40) == (0 % 40) == 0
        #  60: ((60 - 20) % 40) == (40 % 40) == 0
        # 100: ((100 - 20) % 40) == (80 % 40) == 0
        # 140: ((140 - 20) % 40) == (120 % 40) == 0
        # 180: ((180 - 20) % 40) == (160 % 40) == 0
        # 220: ((220 - 20) % 40) == (200 % 40) == 0
        if ((cycle_count - 20) % 40 == 0):
            signal_strength += (cycle_count * registers['X'])


print(f'Signal strength = {signal_strength}')
