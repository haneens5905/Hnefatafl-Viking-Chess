# integer constants to represent each type of piece on the board
EMPTY = 0
ATTACKER = 1
DEFENDER = 2
KING = 3

# the board is 11 rows by 11 columns
BOARD_SIZE = 11

# store the row and column of the throne (center square)
THRONE_ROW = 5
THRONE_COL = 5
THRONE = (THRONE_ROW, THRONE_COL)

# store the four corner positions in a list of tuples
CORNERS = [
    (0, 0),
    (0, BOARD_SIZE - 1),
    (BOARD_SIZE - 1, 0),
    (BOARD_SIZE - 1, BOARD_SIZE - 1)
]


def create_initial_board():
    # builds and returns the starting 11x11 board as a 2d list
    # each cell holds one of: EMPTY, ATTACKER, DEFENDER, or KING

    # create an 11x11 grid filled with EMPTY (0)
    board = []
    for row in range(BOARD_SIZE):
        new_row = []
        for col in range(BOARD_SIZE):
            new_row.append(EMPTY)
        board.append(new_row)

    # list all 24 attacker starting positions (4 groups of 6 on each edge)
    attacker_positions = [
        # top group
        (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
        (1, 5),

        # bottom group
        (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
        (9, 5),

        # left group
        (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
        (5, 1),

        # right group
        (3, 10), (4, 10), (5, 10), (6, 10), (7, 10),
        (5, 9)
    ]

    # place each attacker on the board
    for row, col in attacker_positions:
        board[row][col] = ATTACKER

    # list all 12 defender starting positions (cross shape around the king)
    defender_positions = [
        (3, 5), (4, 5),
        (6, 5), (7, 5),
        (5, 3), (5, 4),
        (5, 6), (5, 7),
        (4, 4), (4, 6),
        (6, 4), (6, 6)
    ]

    # place each defender on the board
    for row, col in defender_positions:
        board[row][col] = DEFENDER

    # place the king on the throne
    board[THRONE_ROW][THRONE_COL] = KING

    return board


def copy_board(board):
    # creates and returns a deep copy of the board
    # changes to the copy will NOT affect the original

    # copy each row using slice notation
    new_board = []
    for row in board:
        new_board.append(row[:])
    return new_board


def get_piece(board, row, col):
    # returns the value stored at position (row, col) on the board
    return board[row][col]


def is_empty(board, row, col):
    # returns true if the square at (row, col) has no piece on it
    return board[row][col] == EMPTY


def is_corner(row, col):
    # returns true if (row, col) matches any of the four corner positions
    return (row, col) in CORNERS


def is_throne(row, col):
    # returns true if (row, col) matches the throne position
    return row == THRONE_ROW and col == THRONE_COL


def is_within_bounds(row, col):
    # returns true if (row, col) is inside the 11x11 grid
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def is_king(board, row, col):
    # returns true if the piece at (row, col) is the king
    return board[row][col] == KING


def find_king(board):
    # loops through every square and returns the king's (row, col)
    # returns none if the king is not on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == KING:
                return (row, col)
    return None


def check_king_escaped(board):
    # returns true if the king is currently standing on a corner square

    # find where the king is
    king_pos = find_king(board)

    # if the king is not on the board, return false
    if king_pos is None:
        return False

    # unpack the king's row and column
    king_row, king_col = king_pos

    # check if the king is on any corner
    if is_corner(king_row, king_col):
        return True

    return False


def _is_hostile_to_king(board, row, col):
    # returns true if a square counts as blocking the king for capture purposes
    # hostile squares: off-board edges, attackers, the empty throne, and corners

    # a position outside the board is treated as a wall
    if not is_within_bounds(row, col):
        return True

    # an attacker piece blocks the king
    if board[row][col] == ATTACKER:
        return True

    # the throne is hostile when the king is not standing on it
    if is_throne(row, col) and board[row][col] != KING:
        return True

    # a corner square is hostile
    if is_corner(row, col):
        return True

    # everything else (empty square or defender) is not hostile
    return False


def check_king_captured(board):
    # returns true if all four neighbors of the king are hostile
    # walls count as hostile, so this covers all three capture cases:
    # surrounded on 4 sides, against a wall with 3 sides, against a corner with 2 sides

    # find where the king is
    king_pos = find_king(board)

    # if king is missing from the board, treat as captured
    if king_pos is None:
        return True

    # unpack the king's row and column
    king_row, king_col = king_pos

    # if the king is on a corner, he escaped so he is not captured
    if is_corner(king_row, king_col):
        return False

    # check all four directions: up, down, left, right
    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    # if any neighbor is not hostile, the king is not fully surrounded
    for d_row, d_col in directions:
        neighbor_row = king_row + d_row
        neighbor_col = king_col + d_col
        if not _is_hostile_to_king(board, neighbor_row, neighbor_col):
            return False

    # all four neighbors are hostile, so the king is captured
    return True


def print_board(board):
    # prints the board to the console with row/column numbers and piece symbols

    # print column numbers across the top
    print("     ", end="")
    for col in range(BOARD_SIZE):
        print(f" {col:2d}", end="")
    print()
    print("     " + "---" * BOARD_SIZE)

    # print each row with its row number and piece symbols
    for row in range(BOARD_SIZE):
        print(f"  {row:2d} |", end="")

        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece == ATTACKER:
                symbol = " A "
            elif piece == DEFENDER:
                symbol = " D "
            elif piece == KING:
                symbol = " K "
            elif is_corner(row, col):
                symbol = " * "
            elif is_throne(row, col):
                symbol = " + "
            else:
                symbol = " . "
            print(symbol, end="")

        print(f"| {row}")

    # print column numbers across the bottom
    print("     " + "---" * BOARD_SIZE)
    print("     ", end="")
    for col in range(BOARD_SIZE):
        print(f" {col:2d}", end="")
    print()


# this block only runs when you execute this file directly (not when imported)
if __name__ == "__main__":
    print("=" * 50)
    print("  HNEFATAFL - Initial Board Setup")
    print("=" * 50)
    print()
    print("Legend:  A = Attacker  |  D = Defender  |  K = King")
    print("         * = Corner    |  + = Throne    |  . = Empty")
    print()

    # create the starting board and display it
    board = create_initial_board()
    print_board(board)

    # test the king escape and capture checks
    print()
    print("King escaped?", check_king_escaped(board))
    print("King captured?", check_king_captured(board))

    # test that copy_board creates an independent copy
    board_copy = copy_board(board)
    board_copy[5][5] = EMPTY
    print()
    print("Original board still has king at (5,5)?", is_king(board, 5, 5))
    print("Copied board has king at (5,5)?", is_king(board_copy, 5, 5))