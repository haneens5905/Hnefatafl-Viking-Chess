import math
from board import ATTACKER, DEFENDER, copy_board
from moves import get_all_moves
from game import apply_move, check_game_over
from utility import evaluate


# depth to use for each difficulty level
DIFFICULTY_DEPTH = {
    "easy"  : 1,
    "medium": 3,
    "hard"  : 5,
}


def _normalize_player(player):
    # accepts either the integer constant or a string and returns the integer constant
    if player == ATTACKER or player == "attacker":
        return ATTACKER
    if player == DEFENDER or player == "defender":
        return DEFENDER
    raise ValueError(
        f"[alpha_beta] unknown player '{player}'. expected ATTACKER, DEFENDER, 'attacker', or 'defender'."
    )


def _opponent(player):
    # returns the opposing player
    player = _normalize_player(player)
    if player == ATTACKER:
        return DEFENDER
    else:
        return ATTACKER


def _order_moves(board, moves, player, is_maximizing):
    # sorts moves by their immediate score so better moves are searched first
    # this helps alpha-beta prune more branches
    scored_moves = []

    for move in moves:
        from_row, from_col, to_row, to_col = move
        child_board = copy_board(board)
        apply_move(child_board, from_row, from_col, to_row, to_col)
        score = evaluate(child_board, player)
        scored_moves.append((score, move))

    # sort highest first for maximizing, lowest first for minimizing
    scored_moves.sort(key=lambda item: item[0], reverse=is_maximizing)
    return [move for _, move in scored_moves]


def alpha_beta(board, depth, alpha, beta, is_maximizing, player):
    # recursive alpha-beta pruning search
    # returns the best score achievable from this board state
    player = _normalize_player(player)

    # check if the game is already over at this node
    winner = check_game_over(board)
    if winner is not None:
        if winner == "attacker":
            return math.inf if player == ATTACKER else -math.inf
        if winner == "defender":
            return math.inf if player == DEFENDER else -math.inf

    # at depth 0 we stop searching and just evaluate the board
    if depth == 0:
        return evaluate(board, player)

    # figure out whose turn it is at this node
    current_player = player if is_maximizing else _opponent(player)
    all_moves = get_all_moves(board, current_player)

    # no moves available means the current mover loses
    if not all_moves:
        return -math.inf if is_maximizing else math.inf

    # sort moves so better ones are explored first (improves pruning)
    all_moves = _order_moves(board, all_moves, player, is_maximizing)

    if is_maximizing:
        # maximizing node — find the move with the highest score
        best_value = -math.inf

        for move in all_moves:
            from_row, from_col, to_row, to_col = move
            child_board = copy_board(board)
            apply_move(child_board, from_row, from_col, to_row, to_col)

            value = alpha_beta(child_board, depth - 1, alpha, beta, False, player)
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)

            # beta cut-off — opponent would never allow this
            if beta <= alpha:
                break

        return best_value

    else:
        # minimizing node — find the move with the lowest score
        best_value = math.inf

        for move in all_moves:
            from_row, from_col, to_row, to_col = move
            child_board = copy_board(board)
            apply_move(child_board, from_row, from_col, to_row, to_col)

            value = alpha_beta(child_board, depth - 1, alpha, beta, True, player)
            best_value = min(best_value, value)
            beta = min(beta, best_value)

            # alpha cut-off — we already have a better option
            if beta <= alpha:
                break

        return best_value


def get_best_move(board, player, depth):
    # searches the game tree and returns the single best move for the given player
    player = _normalize_player(player)
    all_moves = get_all_moves(board, player)

    # no legal moves — game should already be over
    if not all_moves:
        return None

    # sort root moves by immediate score before deep search
    all_moves = _order_moves(board, all_moves, player, True)

    best_move = None
    best_value = -math.inf
    alpha = -math.inf
    beta = math.inf

    for move in all_moves:
        from_row, from_col, to_row, to_col = move
        child_board = copy_board(board)
        apply_move(child_board, from_row, from_col, to_row, to_col)

        # first recursive call is a minimizing node (opponent responds)
        value = alpha_beta(child_board, depth - 1, alpha, beta, False, player)

        if value > best_value:
            best_value = value
            best_move = move

        alpha = max(alpha, best_value)

    return best_move


def get_depth_for_difficulty(difficulty):
    # converts a difficulty string to the corresponding search depth
    key = difficulty.strip().lower()
    if key not in DIFFICULTY_DEPTH:
        raise ValueError(
            f"[alpha_beta] unknown difficulty '{difficulty}'. "
            f"choose from: {list(DIFFICULTY_DEPTH.keys())}"
        )
    return DIFFICULTY_DEPTH[key]