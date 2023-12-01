#!/usr/bin/env python3
#
# This task involves writing a very small assembly language interpreter that
# keeps track of a register (X, which starts at 1), provides instructions
# (noop, and addx), and can use those to draw a 3x1 pixel sprite to the
# 40x6 pixel screen.
#
# This is similar to task1.py, except that we'll be drawing that sprite.
# Instead of a signal strength, we're tracking screen X/Y positions. Every
# CPU cycle, we draw one more pixel. That pixel will be on ("#") for any
# sprites.
#
# A sprite's position is dictated by the X register, which defines the middle
# of the sprite. so, X - 1, X, and X + 1 all draw pixels.
#
# The program ends when we've drawn the whole screen.
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


# Mapping of opcode names to (cycle_count, handler).
OPCODES = {
    'noop': (1, _op_noop),
    'addx': (2, _op_addx),
}


# The size of the screen, in "pixels".
SCREEN_WIDTH = 40
SCREEN_HEIGHT = 6


# The registers we're tracking.
#
# This could just be `X`, but I wrote this with a theoretical "we might need
# to support multiple registers!" design.
registers = {
    'X': 1,
}


# Number of cycles we've executed.
cycle_count = 0


# The current screen drawing position.
screen_x = 0
screen_y = 0


# State on the current instruction we're handling.
opcode_handler = None
opcode_cycles_remaining = 0
opcode_values = ()


with open('input', 'r') as fp:
    while screen_y != SCREEN_HEIGHT:
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

        # Draw the current pixel position on the screen. If the X coordinate
        # overlaps the sprite (X represents the middle of the 3-pixel sprite),
        # then we'll draw a "#". Otherwise, we'll draw a ".".
        x = registers['X']

        if x - 1 <= screen_x <= x + 1:
            pixel = '#'
        else:
            pixel = '.'

        print(pixel, end='')

        # Update the next drawing position. If we're at the end of the line,
        # draw a newline and move to the next line.
        screen_x += 1

        if screen_x == SCREEN_WIDTH:
            print()
            screen_x = 0
            screen_y += 1

        opcode_cycles_remaining -= 1
        cycle_count += 1
