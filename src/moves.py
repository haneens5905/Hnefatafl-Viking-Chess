from board import *


def get_valid_moves(board, row, col):
    # returns a list of all squares this piece can legally move to
    moves = []
    piece = get_piece(board, row, col)

    directions = [
        (-1, 0),  # up
        (1, 0),   # down
        (0, -1),  # left
        (0, 1)    # right
    ]

    for d_row, d_col in directions:
        current_row = row + d_row
        current_col = col + d_col

        while is_within_bounds(current_row, current_col):

            # stop if any piece is blocking (friend or enemy)
            if not is_empty(board, current_row, current_col):
                break

            # stop if regular piece tries to land on throne
            if is_throne(current_row, current_col) and piece != KING:
                break

            # stop if regular piece tries to land on corner
            if is_corner(current_row, current_col) and piece != KING:
                break

            # skip if landing here would immediately sandwich this piece
            temp_board = copy_board(board)
            temp_board[row][col] = EMPTY
            temp_board[current_row][current_col] = piece
            if _would_be_captured_at(temp_board, current_row, current_col, piece):
                current_row += d_row
                current_col += d_col
                continue

            # valid square — add it
            moves.append((current_row, current_col))

            # move to the next square in the same direction
            current_row += d_row
            current_col += d_col

    return moves


def _would_be_captured_at(board, row, col, piece):
    # returns true if a piece landing at (row, col) would be immediately sandwiched
    # the king is handled separately so we skip him here
    if piece == KING:
        return False

    # determine who the enemies are for this piece
    enemy = DEFENDER if piece == ATTACKER else ATTACKER

    def hostile(r, c):
        # wall counts as hostile
        if not is_within_bounds(r, c):
            return True
        # king is unarmed — never counts as hostile even when on the throne
        if is_king(board, r, c):
            return False
        # corner always counts as hostile
        if is_corner(r, c):
            return True
        # throne only counts as hostile when empty
        if is_throne(r, c) and is_empty(board, r, c):
            return True
        # enemy piece counts as hostile
        return board[r][c] == enemy

    # check if the piece is sandwiched horizontally or vertically
    horizontal = hostile(row, col - 1) and hostile(row, col + 1)
    vertical = hostile(row - 1, col) and hostile(row + 1, col)
    return horizontal or vertical


def get_all_moves(board, player):
    # returns a list of every possible move for all pieces belonging to the player
    # each move is stored as (from_row, from_col, to_row, to_col)
    all_moves = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = get_piece(board, row, col)

            # check if this piece belongs to the current player
            # attackers only have one piece type
            # defenders have two: regular defenders and the king
            if player == ATTACKER:
                belongs_to_player = (piece == ATTACKER)
            else:
                belongs_to_player = (piece == DEFENDER or piece == KING)

            # only generate moves for pieces that belong to this player
            if belongs_to_player:
                valid_moves = get_valid_moves(board, row, col)

                # add each destination as a full move tuple
                for to_row, to_col in valid_moves:
                    all_moves.append((row, col, to_row, to_col))

    return all_moves


def is_hostile(board, row, col, player):
    # king is never hostile (unarmed) — check this first before anything else
    if is_within_bounds(row, col) and is_king(board, row, col):
        return False

    # out of bounds counts as hostile (wall)
    if not is_within_bounds(row, col):
        return True

    # your own piece is hostile
    piece = get_piece(board, row, col)
    if player == ATTACKER and piece == ATTACKER:
        return True
    if player == DEFENDER and piece == DEFENDER:
        return True

    # empty throne is hostile
    if is_throne(row, col) and is_empty(board, row, col):
        return True

    # corner is hostile
    if is_corner(row, col):
        return True

    # everything else is not hostile
    return False


def check_captures(board, row, col, player):
    # king is unarmed — he cannot perform sandwich captures
    if player == DEFENDER and is_king(board, row, col):
        return

    # after a piece moves to (row, col), check all 4 directions for any sandwiched opponent pieces
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for d_row, d_col in directions:
        neighbor_row = row + d_row
        neighbor_col = col + d_col
        beyond_row = row + d_row * 2
        beyond_col = col + d_col * 2

        # skip if neighbor is out of bounds
        if not is_within_bounds(neighbor_row, neighbor_col):
            continue

        # skip if neighbor has no opponent piece
        neighbor_piece = get_piece(board, neighbor_row, neighbor_col)
        if player == ATTACKER and neighbor_piece not in (DEFENDER, KING):
            continue
        if player == DEFENDER and neighbor_piece != ATTACKER:
            continue

        # skip if neighbor is the king (king capture is handled separately)
        if is_king(board, neighbor_row, neighbor_col):
            continue

        # if the square beyond the opponent is hostile, the opponent is sandwiched — remove it
        if is_hostile(board, beyond_row, beyond_col, player):
            board[neighbor_row][neighbor_col] = EMPTY