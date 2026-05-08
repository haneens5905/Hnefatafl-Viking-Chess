from board import (
    find_king,
    is_throne,
    _is_hostile_to_king,
    BOARD_SIZE,
    ATTACKER,
    DEFENDER,
    CORNERS
)
from moves import get_valid_moves

# weights control how much each factor influences the score
PIECE_WEIGHT = 4            # importance of piece count advantage
DISTANCE_WEIGHT = 6         # importance of king's closeness to corners
MOBILITY_WEIGHT = 6         # importance of how freely the king can move
ESCAPE_WEIGHT = 30          # strongest factor — king having a clear escape path
ENCIRCLEMENT_WEIGHT = 12    # importance of how surrounded the king is


def count_pieces(board):
    # counts and returns the number of attackers and defenders on the board
    attackers = 0
    defenders = 0

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == ATTACKER:
                attackers += 1
            elif board[r][c] == DEFENDER:
                defenders += 1

    return attackers, defenders


def piece_count_score(board):
    # returns a score based on piece count — more defenders = better for defenders
    attackers, defenders = count_pieces(board)
    return (defenders - attackers) * PIECE_WEIGHT


def king_distance_score(board):
    # returns a score based on how close the king is to the nearest corner
    # closer king = higher score for defenders
    king_pos = find_king(board)

    # king missing means defenders lost
    if king_pos is None:
        return -1000

    kr, kc = king_pos

    # compute manhattan distance to all four corners
    distances = [
        abs(kr - cr) + abs(kc - cc)
        for cr, cc in CORNERS
    ]

    # use the closest corner
    min_dist = min(distances)

    # closer distance = higher score
    return (20 - min_dist) * DISTANCE_WEIGHT


def king_mobility_score(board):
    # returns a score based on how many squares the king can currently move to
    king_pos = find_king(board)

    # king missing means defenders lost
    if king_pos is None:
        return -1000

    r, c = king_pos

    # get all possible moves for the king
    moves = get_valid_moves(board, r, c)

    # king with no moves gets a penalty
    if len(moves) == 0:
        return -20

    # more moves = more flexibility
    return len(moves) * MOBILITY_WEIGHT


def is_path_clear(board, start, end):
    # returns true if there is a clear straight-line path between two squares
    sr, sc = start
    er, ec = end

    # only straight-line movement is allowed (rook-like)
    if sr != er and sc != ec:
        return False

    # check horizontal path
    if sr == er:
        step = 1 if ec > sc else -1
        for col in range(sc + step, ec, step):
            # path must be empty (throne counts as passable for king escape checks)
            if not (board[sr][col] == 0 or is_throne(sr, col)):
                return False

    # check vertical path
    else:
        step = 1 if er > sr else -1
        for row in range(sr + step, er, step):
            if not (board[row][sc] == 0 or is_throne(row, sc)):
                return False

    return True


def king_escape_score(board):
    # returns a score based on how many clear straight-line paths the king has to corners
    king_pos = find_king(board)

    # king missing means defenders lost
    if king_pos is None:
        return -1000

    score = 0

    # check each corner — clear path to corner is rewarded heavily
    for corner in CORNERS:
        if is_path_clear(board, king_pos, corner):
            score += ESCAPE_WEIGHT

    return score


def king_encirclement_score(board):
    # returns a score based on how many sides of the king are blocked by hostile squares
    # more blocked sides = worse for defenders
    king_pos = find_king(board)

    # king missing means defenders lost
    if king_pos is None:
        return -1000

    r, c = king_pos
    blocked = 0

    # check all 4 directions around the king
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc

        # use shared logic to detect hostile squares (attackers, walls, throne, corners)
        if _is_hostile_to_king(board, nr, nc):
            blocked += 1

    # more blocked sides = lower score for defenders
    return -blocked * ENCIRCLEMENT_WEIGHT


def evaluate(board, player):
    # combines all factors into a single score for the given player
    # higher score = better position for that player
    score = 0

    score += piece_count_score(board)
    score += king_distance_score(board)
    score += king_mobility_score(board)
    score += king_escape_score(board)
    score += king_encirclement_score(board)

    # all factors are calculated from the defender's perspective
    # attacker gets the opposite score
    return -score if player == ATTACKER else score


# run a quick sanity check when this file is executed directly
if __name__ == "__main__":
    from board import create_initial_board

    board = create_initial_board()
    print("Evaluation (Defender):", evaluate(board, DEFENDER))
    print("Evaluation (Attacker):", evaluate(board, ATTACKER))