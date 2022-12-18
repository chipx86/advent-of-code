#!/usr/bin/env python3
#
# TETRIS! Basically.
#
# I love Tetris. I still play Gameboy Tetris. Tetris DX. Tetris 99. Tetris
# Effect. Tetris: The Grand Master. Tetris is great.
#
# Anyway, I liked this puzzle. It wasn't bad. Kind of fun.
#
# In this task, we have a series of shapes that appear in the same order. They
# don't rotate, they just move left or right and drop by 1 until they settle
# (just like Tetris). The input data are the left/right movements, and they
# loop. We have to figure out how high our stack is after 2,022 moves.
#
# The width of the column is 7, and the height is ever-expanding. So I made
# two choices:
#
# 1. All rows (for the board and the shapes) are going to be 1-byte bitmasks.
#    This is super efficient! Minimal storage, and it makes collision detection
#    really easy.
#
# 2. The board's 0 position will be the bottom. Basically, the board grows
#    upward, index-wise. This makes it easy to expand the board.
#
# So, for movement, we need to do the following in order:
#
# 1. Check whether we're moving left or right.
#
# 2. Move that direction, if we can. If we bump up against a wall or a piece,
#    cancel the move. Otherwise, place the piece in that new location.
#
# 3. Move down one, if we can. If we bump up against the floor or a piece,
#    cancel the move. We're done with that piece. Otherwise, place the piece
#    in that new location.
#
# Very straight-forward.
#
# Now let's talk about the bitmask representations.
#
# Because the width fits in a byte (it's only 7 wide), and every cell is either
# on or off (rock or air), a bitmask is perfect. 1 is rock, 0 is air.
#
# We assume the left-most extent of the shape is its X, and the top-most is Y.
# Y drops by 1 every time we go down. X drops by 1 when going left, or
# increases by 1 if going right.
#
# To calculate the bitmask for placing a row of a shape at a given X:
#
#    place_bitmask[y] = shape_bitmask[y] << (BOARD_WIDTH - (shape_width + x))
#
#    That must be done for each row in the shape.
#
# To calculate the new row bitmask with a piece added:
#
#    new_row[y] = row_bitmask[y] | place_bitmask[y]
#
# To remove a shape from a row, XOR it from the row:
#
#    new_row[y] = row_bitmask[y] ^ place_bitmask[y]
#
# To test for collision, AND it and compare:
#
#    collided[y] = ((row_bitmask[y] & place_bitmask[y]) == row_bitmask[y])
#
# This is all really fast and easy.


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
MAX_PLACED_PIECES = 2022


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
    """
    # Track the current piece, position, and next piece.
    cur_piece = None
    piece_x = 0
    piece_y = 0
    next_piece_i = 0

    # Track the populated height of the board, how many pieces we placed,
    # and any extra height we'll tack onto the final answer.
    populated_height = 0
    num_placed_pieces = 0

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

    print('Tower of rocks = %s tall' % (populated_height))


if __name__ == '__main__':
    main()
