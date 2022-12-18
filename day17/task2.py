#!/usr/bin/env python3
#
# MORE TETRIS!
#
# See task1.py for the main details. And then we'll go into the rest of this.
#
# Okay, so Task 2 requires we go up to 1 trillion rows. That's a lot. So
# obviously, there's a trick.
#
# I figured, okay, things repeat. I first tried to write code that looks for a
# new floor (a solid row of rocks), but that wasn't the solution.
#
# So I tweaked the code to be more general, to look for any repeating pattern,
# taking into account:
#
# 1. A gust instruction index.
# 2. A piece index.
# 3. The position of rocks on the top-most row of the board.
#
# Any time we place a piece, we store some cached data. Within that is a
# second cache of diffs between previous encounters of that cached data. As
# soon as we find a second occurrence of the same diff, we determine we found
# an actual reliable cycle.
#
# If we do find a cycle, we can use that along with MATH to extrapolate the
# max height we can reach based on what was accomplished during that cycle and
# the number of pieces that remain to be processed.


# The list of all our pieces, their dimensions, and their shape, in order of
# appearance.
PIECES = [
    {
        'width': 4,
        'height': 1,
        'shape': [
            0b1111,
        ],
    },
    {
        'width': 3,
        'height': 3,
        'shape': [
            0b010,
            0b111,
            0b010,
        ],
    },
    {
        'width': 3,
        'height': 3,
        'shape': [
            0b001,
            0b001,
            0b111,
        ],
    },
    {
        'width': 1,
        'height': 4,
        'shape': [
            0b1,
            0b1,
            0b1,
            0b1,
        ],
    },
    {
        'width': 2,
        'height': 2,
        'shape': [
            0b11,
            0b11,
        ],
    },
]


# A mapping of movement instructions to relative X offsets.
MOVEMENT = {
    b'<': -1,
    b'>': 1,
}

# The width of the board.
BOARD_WIDTH = 7

# The absolute X and relative Y positions for all new pieces.
PIECE_START_X = 2
PIECE_START_Y_DIST = 3

# The number of pieces we need to place before the task ends.
MAX_PLACED_PIECES = 1_000_000_000_000


# The board, as a row of bitmasks, with index 0 being the floor.
board = []


def move_piece(*, piece, new_x, new_y, old_x=None, old_y=None):
    """Move a piece to a new location.

    This can either place a new piece for the first time, or move a piece from
    an old location to a new one.

    This will check for collision as part of the process. If the piece were to
    collide, the piece won't move at all, and a collision flag will be set.

    Args:
        piece (dict):
            The piece information to place.

        new_x (int):
            The new X location for the piece.

        new_y (int):
            The new Y location for the piece.

        old_x (int, optional):
            The X location for a piece, when moving an existing piece.

        old_y (int, optional):
            The Y location for a piece, when moving an existing piece.

    Returns:
        tuple:
        A 3-tuple of:

        Tuple:
            0 (bool):
                Whether the piece collided.

            1 (int):
                The resulting X location.

            2 (int):
                The resulting Y location.
    """
    assert new_x is not None
    assert new_y is not None

    piece_width = piece['width']
    piece_height = piece['height']
    piece_shape = piece['shape']

    if old_x is not None:
        # We're moving a piece from an old location. Remove it from the
        # affected rows.
        #
        # We'll remove with a bitwise XOR.
        assert old_y is not None

        old_shift = BOARD_WIDTH - (piece_width + old_x)

        for y in range(piece_height):
            board[old_y - y] ^= (piece_shape[y] << old_shift)

    # Define our bitshift for the new location of the piece.
    new_shift = BOARD_WIDTH - (piece_width + new_x)

    # Check for collision. We collide if we tried to go through the floor or
    # through another shape.
    #
    # We'll test with a bitwise AND.
    collides = (
        new_y - piece_height + 1 < 0 or
        any(
            (board[new_y - y] & (piece_shape[y] << new_shift)) != 0
            for y in range(piece_height)
        )
    )

    if collides:
        # We collided. Don't actually shift the piece. We'll revert back to
        # the old position and re-compute the shift width.
        assert old_x is not None

        new_x = old_x
        new_y = old_y
        new_shift = BOARD_WIDTH - (piece_width + new_x)

    # Place the piece at the target location.
    #
    # We'll use a bitwise OR for this.
    for y in range(piece_height):
        board[new_y - y] |= (piece_shape[y] << new_shift)

    return collides, new_x, new_y


def main():
    """Main logic for the program.

    This will run through the Tetris-style simulation, reading pieces, placing
    them on the board, running through movement until they land, checking the
    number of pieces placed, and doing it all over again.

    There's an outer loop for processing until we hit the target row height,
    and an inner loop for handling movement.

    There's also some cycle checks, to find out when we hit a repeatable
    pattern and to infer the values after that, since we have such a massive
    row count we're aiming for.
    """
    # State for checking for repeated cycles of the same patterns.
    cycle_checks = {}
    found_cycle = False

    # Track the current index in the gust pattern.
    gust_i = 0

    # Track the current piece, position, and next piece.
    cur_piece = None
    piece_x = 0
    piece_y = 0
    next_piece_i = 0

    # Track the populated height of the board, how many pieces we placed,
    # and any extra height we'll tack onto the final answer.
    populated_height = 0
    num_placed_pieces = 0
    populated_height_extra = 0

    with open('input', 'rb') as fp:
        while True:
            assert cur_piece is None

            # It's time to select a new piece and place it.
            cur_piece = PIECES[next_piece_i]
            piece_height = cur_piece['height']

            # Set the new piece locations. This will always start at the
            # same X position, and the same Y relative to the highest
            # point on the board.
            piece_x = PIECE_START_X
            piece_y = (populated_height + PIECE_START_Y_DIST +
                       piece_height - 1)

            # Extend the board as necessary, so there's room for the piece
            # to fit.
            if piece_y + 1 > len(board):
                board.extend([0] * (piece_y - len(board) + 1))

            # Draw the piece on the board.
            move_piece(piece=cur_piece,
                       new_x=piece_x,
                       new_y=piece_y)

            # Select the next piece, for the next time we're here.
            next_piece_i += 1

            if next_piece_i == len(PIECES):
                next_piece_i = 0

            # Begin our movement loop.
            while True:
                # Read the next instruction to determine which direction to move.
                instruction = fp.read(1)

                if instruction in (b'', b'\n'):
                    # We hit the end of the input. Reset and try again.
                    fp.seek(0)
                    instruction = fp.read(1)

                    gust_i = 0

                gust_i += 1

                # Figure out the next X location to move. Confine it to the
                # board's dimensions.
                new_piece_x = min(max(0, piece_x + MOVEMENT[instruction]),
                                  BOARD_WIDTH - cur_piece['width'])

                if new_piece_x != piece_x:
                    # Move the piece horizontally. If it can't move, this won't
                    # do anything.
                    collides, piece_x, piece_y = move_piece(
                        piece=cur_piece,
                        old_x=piece_x,
                        old_y=piece_y,
                        new_x=new_piece_x,
                        new_y=piece_y)

                # Now move it vertically. If it collides, we'll place the piece.
                new_piece_y = max(0, piece_y - 1)

                collides, piece_x, piece_y = move_piece(
                    piece=cur_piece,
                    old_x=piece_x,
                    old_y=piece_y,
                    new_x=piece_x,
                    new_y=piece_y - 1)

                if collides:
                    # We collided. The piece is placed!
                    break

            assert collides

            # Now that the piece is placed, we can update our state and then
            # reset for the next piece.
            num_placed_pieces += 1
            populated_height = max(populated_height, piece_y + 1)
            cur_piece = None

            if num_placed_pieces == MAX_PLACED_PIECES:
                # There are no more pieces needed. We're done!
                break

            # Ideally, we want to find a cycle, so we don't process 1 trillion
            # rows. But we only want to do it once.
            if not found_cycle:
                # Our key will incorporate the wind gust (movement) index,
                # the next piece index (in other words, what piece we're on),
                # and the bitmask of the top populated row of the board.
                key = (gust_i, next_piece_i, board[populated_height - 1])
                assert key[-1] != 0

                try:
                    cycle_info = cycle_checks[key]
                except KeyError:
                    cycle_info = {
                        'last_num_placed': None,
                        'diffs': {},
                    }
                    cycle_checks[key] = cycle_info

                last_num_placed = cycle_info['last_num_placed']
                cycle_info['last_num_placed'] = num_placed_pieces
                diffs = cycle_info['diffs']

                # We're looking for a repeated pattern yielding the same
                # difference between values. We can't just trust the first
                # time we find our key in cycle_info. We need to pair that
                # with the difference between our number of placed pieces.
                # That's the key we'll use for this state.
                diff = num_placed_pieces - (last_num_placed or 0)

                try:
                    diff_info = diffs[diff]
                    found_cycle = True
                except KeyError:
                    diffs[diff] = (num_placed_pieces, populated_height)

                if found_cycle:
                    # We found a cycle! We're going to update some stuff.
                    cycle_num_placed_pieces, cycle_populated_height = diff_info

                    # Here's how many pieces still remain to be placed.
                    num_remaining_pieces = MAX_PLACED_PIECES - num_placed_pieces

                    # Extrapolate from here and figure out what the populated
                    # height would be at if completing the number of available
                    # full cycles.
                    multiplier = \
                        num_remaining_pieces // cycle_num_placed_pieces
                    populate_height_extra = (
                        multiplier *
                        (populated_height - cycle_populated_height))

                    # Figure out how many pieces we'd have placed at that
                    # height.
                    num_placed_pieces += cycle_num_placed_pieces * multiplier

    print('Tower of rocks = %s tall'
          % (populated_height + populate_height_extra))


if __name__ == '__main__':
    main()
